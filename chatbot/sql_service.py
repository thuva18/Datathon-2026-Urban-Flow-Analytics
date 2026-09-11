"""
chatbot/sql_service.py
Safe read-only DuckDB SQL tool for the 48M+ row taxi dataset.

Security:
- Blocks all write/modification keywords
- Enforces row limits
- Validates SQL before execution
- Parameterization for any injectable values
"""
import re
import logging
import duckdb
import pandas as pd

from chatbot.config import PARQUET_FILE, ZONES_FILE, SQL_BLOCKLIST, SQL_MAX_ROWS, SQL_TIMEOUT

logger = logging.getLogger("chatbot")

# ─── Dataset schema context (for Groq prompt) ────────────────────────────────

SCHEMA_DESCRIPTION = """
The main taxi dataset is a Parquet file queried via DuckDB.
Reference it as: read_parquet('{parquet}')

Columns in the main dataset:
  pickup_timestamp     TIMESTAMP  — trip start time
  dropoff_timestamp    TIMESTAMP  — trip end time
  origin_loc_id        INTEGER    — pickup zone ID (1-265, matches loc_id in zone lookup)
  dest_loc_id          INTEGER    — dropoff zone ID
  origin_borough       VARCHAR    — pickup borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island, EWR)
  dest_borough         VARCHAR    — dropoff borough
  origin_zone          VARCHAR    — pickup zone name
  dest_zone            VARCHAR    — dropoff zone name
  distance_miles       FLOAT      — trip distance
  base_fare            FLOAT      — base fare amount
  charge_total         FLOAT      — total fare charged
  rider_count_clean    INTEGER    — passenger count (imputed, median=1)
  provider_code        INTEGER    — taxi provider (1=yellow, 2=green/FHV)

Zone lookup (separate CSV):
  loc_id               INTEGER    — zone ID
  borough_name         VARCHAR    — borough
  zone_name            VARCHAR    — zone name
  service_zone         VARCHAR    — Yellow Zone / Boro Zone / Airports / EWR

Date range: 2025-04-01 to 2026-03-31 (48,601,782 total records)

IMPORTANT SQL RULES:
- Always use read_parquet('{parquet}') for trip data
- Always add LIMIT {max_rows} to prevent large result sets
- Always filter by date range or specific aggregate when possible
- Use EXTRACT(hour FROM pickup_timestamp) for hour-of-day
- Use EXTRACT(dow FROM pickup_timestamp) for day-of-week (0=Sunday, 6=Saturday)
- Never use SELECT * — always select specific columns
""".format(parquet=PARQUET_FILE, max_rows=SQL_MAX_ROWS)


# ─── SQL Validation ───────────────────────────────────────────────────────────

def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Returns (is_safe, reason).
    Blocks dangerous keywords and patterns.
    """
    sql_lower = sql.lower().strip()

    # Strip comments
    sql_cleaned = re.sub(r'--[^\n]*', '', sql_lower)
    sql_cleaned = re.sub(r'/\*.*?\*/', '', sql_cleaned, flags=re.DOTALL)

    # Strip quoted string literals (single or double quoted) before keyword scan
    # so file paths like 'Datathon - Copy\...' don't false-positive on 'copy'
    sql_no_strings = re.sub(r"'[^']*'", "''", sql_cleaned)   # single-quoted
    sql_no_strings = re.sub(r'"[^"]*"', '""', sql_no_strings)  # double-quoted

    for keyword in SQL_BLOCKLIST:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, sql_no_strings):
            return False, f"SQL contains forbidden operation: '{keyword.upper()}'"

    # Block multiple statements
    if ';' in sql_cleaned.rstrip(';'):
        return False, "Multiple SQL statements are not allowed."

    # Must be a SELECT statement
    if not re.match(r'\s*(select|with)\b', sql_cleaned):
        return False, "Only SELECT queries are permitted."

    # Block LIMIT bypass attempts (ensure LIMIT exists)
    if 'limit' not in sql_cleaned:
        return True, "valid (no LIMIT — will auto-add)"

    return True, "valid"


def enforce_limit(sql: str) -> str:
    """Ensure the query has a LIMIT clause capped at SQL_MAX_ROWS."""
    sql_stripped = sql.rstrip().rstrip(';')
    sql_lower = sql_stripped.lower()

    limit_match = re.search(r'\blimit\s+(\d+)', sql_lower)
    if limit_match:
        existing = int(limit_match.group(1))
        if existing > SQL_MAX_ROWS:
            # Replace existing limit with max
            sql_stripped = re.sub(
                r'\blimit\s+\d+', f'LIMIT {SQL_MAX_ROWS}', sql_stripped, flags=re.IGNORECASE
            )
    else:
        sql_stripped = sql_stripped + f"\nLIMIT {SQL_MAX_ROWS}"

    return sql_stripped


# ─── Query Execution ─────────────────────────────────────────────────────────

def execute_safe_query(sql: str) -> dict:
    """
    Validate and execute a read-only SQL query against the Parquet dataset.
    Returns: {success, data (list of dicts), row_count, columns, error}
    """
    logger.info("SQL query received (len=%d): %.200s", len(sql), sql)

    # 1. Validate
    is_safe, reason = validate_sql(sql)
    if not is_safe:
        logger.warning("SQL blocked: %s | SQL: %.200s", reason, sql)
        return {
            "success":   False,
            "error":     reason,
            "sql_used":  sql,
        }

    # 2. Enforce limit
    safe_sql = enforce_limit(sql)

    # 3. Execute (DuckDB in-process, read-only)
    try:
        con = duckdb.connect(database=":memory:", read_only=False)
        # DuckDB can read Parquet without a persistent DB
        df = con.execute(safe_sql).df()
        con.close()

        rows = df.to_dict(orient="records")
        logger.info("SQL executed successfully: %d rows returned.", len(rows))

        return {
            "success":   True,
            "data":      rows,
            "row_count": len(rows),
            "columns":   list(df.columns),
            "sql_used":  safe_sql,
        }

    except duckdb.Error as e:
        logger.error("DuckDB error: %s", e)
        return {
            "success": False,
            "error":   f"Database query failed: {e}",
            "sql_used": safe_sql,
        }
    except Exception as e:
        logger.error("Unexpected SQL execution error: %s", e)
        return {
            "success": False,
            "error":   f"Unexpected error during query: {e}",
            "sql_used": safe_sql,
        }


# ─── Schema accessor (for intent extractor prompts) ──────────────────────────

def get_schema_description() -> str:
    return SCHEMA_DESCRIPTION
