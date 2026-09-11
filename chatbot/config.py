"""
chatbot/config.py — Central configuration for Urban Flow Analytics chatbot.
Loads paths, env vars, and constants.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ─── Paths ───────────────────────────────────────────────────────────────────
PARQUET_FILE = str(_PROJECT_ROOT / "urban_flow_analytics_merged.parquet")
ZONES_FILE   = str(_PROJECT_ROOT / "Urban_Flow_Analytics_Zone_Dataset.csv")
MODELS_DIR   = str(_PROJECT_ROOT / "models")
README_FILE  = str(_PROJECT_ROOT / "README.md")
DATA_DICT_FILE = str(_PROJECT_ROOT / "Data_Dictionary.pdf")

MODEL_PATHS = {
    "fare":     os.path.join(MODELS_DIR, "fare_prediction_model.pkl"),
    "duration": os.path.join(MODELS_DIR, "duration_prediction_model.pkl"),
    "demand":   os.path.join(MODELS_DIR, "demand_forecasting_model.pkl"),
    "cluster":  os.path.join(MODELS_DIR, "zone_clustering_model.pkl"),
}

# ─── Groq ────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Groq-recommended current production models (Sept 2026).
# Ordered best→fastest. The probe tests each with a real completion call.
GROQ_MODEL_PREFERENCE = [
    "openai/gpt-oss-20b",   # Fast — confirmed free-tier accessible
    "qwen/qwen3.6-27b",     # Alternative — confirmed free-tier accessible
    "openai/gpt-oss-120b",  # Groq flagship (higher-tier accounts)
    "qwen/qwen3.8-27b",     # Preview fallback
]

def _resolve_groq_model() -> str:
    """
    Find the first model in GROQ_MODEL_PREFERENCE that your API key can
    actually call by issuing a minimal test completion for each candidate.
    This is the only reliable way — the /models endpoint lists models your
    key cannot access (paid-tier models appear there too).
    """
    import logging as _logging
    _log = _logging.getLogger("chatbot")

    if not GROQ_API_KEY:
        _log.warning("GROQ_API_KEY not set — chatbot will not use LLM.")
        return GROQ_MODEL_PREFERENCE[0]

    try:
        from groq import Groq as _Groq, APIError as _APIError
    except ImportError:
        _log.warning("groq package not installed; skipping model probe.")
        return GROQ_MODEL_PREFERENCE[0]

    client = _Groq(api_key=GROQ_API_KEY)
    for model in GROQ_MODEL_PREFERENCE:
        try:
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            _log.info(f"Groq model auto-selected (verified): {model}")
            return model
        except Exception as exc:
            _log.warning(f"Groq model {model!r} not accessible: {exc}")

    _log.error("No Groq model was accessible — falling back to first in list.")
    return GROQ_MODEL_PREFERENCE[0]

GROQ_MODEL = _resolve_groq_model()   # verified once at startup

# ─── SQL Safety ──────────────────────────────────────────────────────────────
SQL_BLOCKLIST = [
    "insert", "update", "delete", "drop", "alter",
    "truncate", "create", "attach", "copy",
    "pragma", "into outfile", "load_extension",
    "read_csv", "read_json",        # prevent arbitrary FS reads
    "write_parquet", "export",      # prevent FS writes
    "shell", "system",              # prevent shell execution
]
SQL_MAX_ROWS = 500
SQL_TIMEOUT  = 30  # seconds

# ─── Zone Cluster Labels (from README / notebook analysis) ───────────────────
CLUSTER_LABELS = {
    0: "Morning Commuter Hub",
    1: "Daytime Commercial District",
    2: "Evening Dining & Entertainment Hub",
    3: "Quiet Residential / Peripheral Zone",
}

# ─── Dataset Date Range ──────────────────────────────────────────────────────
DATASET_START = "2025-04-01"
DATASET_END   = "2026-03-31"

# ─── Logging ─────────────────────────────────────────────────────────────────
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] chatbot.%(module)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("chatbot")
