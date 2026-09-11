"""
chatbot/model_services.py
Wrapper services for the four Urban Flow Analytics print models.

Model inputs (from app.py and Gravitons notebook):
  Fare:     pickup_month, pickup_dow, pickup_hour, is_weekend, is_rush_hour,
            origin_loc_id, dest_loc_id, provider_code, rider_count_clean,
            estimated_route_distance
  Duration: distance_miles, log_distance, hist_od_duration_prior,
            hist_od_pace_prior, origin_borough, dest_borough, period_type,
            pickup_hour, pickup_dow, is_intra_borough, is_airport_trip
  Demand:   loc_id + lag features (lag_24h, lag_48h, lag_72h, lag_168h,
            rolling_mean_24h)  computed from Parquet
  Cluster:  24-hour diurnal demand profile per zone (24 values)
"""
import logging
import math
import numpy as np
import pandas as pd
import duckdb
import joblib

from chatbot.config import PARQUET_FILE, ZONES_FILE, MODEL_PATHS, CLUSTER_LABELS

logger = logging.getLogger("chatbot")

# ─── Cached model & zone data loading ────────────────────────────────────────

_fare_model     = None
_duration_model = None
_demand_model   = None
_cluster_model  = None
_zones_df       = None


def _get_zones() -> pd.DataFrame:
    global _zones_df
    if _zones_df is None:
        _zones_df = pd.read_csv(ZONES_FILE)
    return _zones_df


def _get_fare_model():
    global _fare_model
    if _fare_model is None:
        _fare_model = joblib.load(MODEL_PATHS["fare"])
        logger.info("Fare print model loaded.")
    return _fare_model


def _get_duration_model():
    global _duration_model
    if _duration_model is None:
        _duration_model = joblib.load(MODEL_PATHS["duration"])
        logger.info("Duration print model loaded.")
    return _duration_model


def _get_demand_model():
    global _demand_model
    if _demand_model is None:
        _demand_model = joblib.load(MODEL_PATHS["demand"])
        logger.info("Demand forecasting print model loaded.")
    return _demand_model


def _get_cluster_model():
    global _cluster_model
    if _cluster_model is None:
        _cluster_model = joblib.load(MODEL_PATHS["cluster"])
        logger.info("Zone clustering print model loaded.")
    return _cluster_model


# ─── Helper: OD stats (leakage-safe historical lookup) ───────────────────────

def _get_od_stats(origin_id: int, dest_id: int):
    """
    Return (avg_dist, avg_duration_prior, avg_pace_prior)
    from historical Parquet data for the OD pair.
    Falls back to (5.0, 15.0, 3.0) if insufficient data.
    """
    query = f"""
    SELECT
        AVG(distance_miles)                                                      AS avg_dist,
        AVG(EXTRACT(epoch FROM (dropoff_timestamp - pickup_timestamp))/60.0)    AS avg_duration,
        AVG(EXTRACT(epoch FROM (dropoff_timestamp - pickup_timestamp))/60.0
            / NULLIF(distance_miles, 0))                                         AS avg_pace
    FROM read_parquet('{PARQUET_FILE}')
    WHERE origin_loc_id = {origin_id}
      AND dest_loc_id   = {dest_id}
      AND distance_miles > 0
      AND distance_miles < 50
    """
    try:
        df = duckdb.query(query).df()
        if df.empty or pd.isna(df["avg_dist"][0]):
            return 5.0, 15.0, 3.0
        return float(df["avg_dist"][0]), float(df["avg_duration"][0]), float(df["avg_pace"][0])
    except Exception as e:
        logger.warning("OD stats query failed: %s", e)
        return 5.0, 15.0, 3.0


# ─── Zone lookup helper ───────────────────────────────────────────────────────

def _zone_row(zone_name: str):
    zones = _get_zones()
    row = zones[zones["zone_name"].str.lower() == zone_name.lower()]
    if row.empty:
        raise ValueError(f"Zone not found: '{zone_name}'")
    return row.iloc[0]


# ─── Period type (matches app.py heuristic) ──────────────────────────────────

def _period_type(hour: int) -> str:
    if hour < 6:
        return "Late Night"
    elif hour < 10:
        return "AM Rush"
    elif hour < 16:
        return "Midday"
    elif hour < 20:
        return "PM Rush"
    else:
        return "Evening"


# ─── 1. Fare Prediction ───────────────────────────────────────────────────────

def predict_fare(
    origin_zone: str,
    dest_zone: str,
    pickup_hour: int,
    pickup_dow: int,
    pickup_month: int,
    rider_count: int = 1,
    provider_code: int = 2,
) -> dict:
    """
    Predict upfront fare for a taxi trip.
    Returns: {predicted_fare, estimated_distance, inputs_used}
    """
    try:
        origin = _zone_row(origin_zone)
        dest   = _zone_row(dest_zone)

        origin_id  = int(origin["loc_id"])
        dest_id    = int(dest["loc_id"])

        avg_dist, _, _ = _get_od_stats(origin_id, dest_id)

        is_weekend  = 1 if pickup_dow >= 5 else 0
        is_rush_hour = 1 if (pickup_dow < 5 and ((7 <= pickup_hour <= 9) or (16 <= pickup_hour <= 19))) else 0

        features = pd.DataFrame([{
            "pickup_month":             pickup_month,
            "pickup_dow":               pickup_dow,
            "pickup_hour":              pickup_hour,
            "is_weekend":               is_weekend,
            "is_rush_hour":             is_rush_hour,
            "origin_loc_id":            origin_id,
            "dest_loc_id":              dest_id,
            "provider_code":            provider_code,
            "rider_count_clean":        rider_count,
            "estimated_route_distance": avg_dist,
        }])

        model = _get_fare_model()
        predicted_fare = float(model.predict(features)[0])

        return {
            "success":            True,
            "predicted_fare":     round(predicted_fare, 2),
            "estimated_distance": round(avg_dist, 2),
            "inputs_used": {
                "origin_zone":   origin_zone,
                "dest_zone":     dest_zone,
                "pickup_hour":   pickup_hour,
                "pickup_dow":    pickup_dow,
                "pickup_month":  pickup_month,
                "rider_count":   rider_count,
                "is_weekend":    bool(is_weekend),
                "is_rush_hour":  bool(is_rush_hour),
            },
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error("Fare prediction error: %s", e)
        return {"success": False, "error": f"Prediction failed: {e}"}


# ─── 2. Duration / ETA Prediction ─────────────────────────────────────────────

def predict_duration(
    origin_zone: str,
    dest_zone: str,
    pickup_hour: int,
    pickup_dow: int,
) -> dict:
    """
    Predict trip duration (minutes) using the duration print model.
    Returns: {predicted_duration_minutes, estimated_distance, inputs_used}
    """
    try:
        origin = _zone_row(origin_zone)
        dest   = _zone_row(dest_zone)

        origin_id  = int(origin["loc_id"])
        dest_id    = int(dest["loc_id"])
        origin_boro = str(origin["borough_name"])
        dest_boro   = str(dest["borough_name"])

        avg_dist, avg_dur_prior, avg_pace_prior = _get_od_stats(origin_id, dest_id)

        is_intra_borough = 1 if origin_boro == dest_boro else 0
        is_airport = 1 if ("airport" in origin_zone.lower() or "airport" in dest_zone.lower()) else 0
        period = _period_type(pickup_hour)

        features = pd.DataFrame([{
            "distance_miles":       avg_dist,
            "log_distance":         math.log1p(avg_dist),
            "hist_od_duration_prior": avg_dur_prior,
            "hist_od_pace_prior":   avg_pace_prior,
            "origin_borough":       origin_boro,
            "dest_borough":         dest_boro,
            "period_type":          period,
            "pickup_hour":          pickup_hour,
            "pickup_dow":           pickup_dow,
            "is_intra_borough":     is_intra_borough,
            "is_airport_trip":      is_airport,
        }])

        model = _get_duration_model()
        predicted_minutes = float(model.predict(features)[0])

        return {
            "success":                    True,
            "predicted_duration_minutes": round(predicted_minutes, 1),
            "estimated_distance":         round(avg_dist, 2),
            "inputs_used": {
                "origin_zone":       origin_zone,
                "dest_zone":         dest_zone,
                "origin_borough":    origin_boro,
                "dest_borough":      dest_boro,
                "pickup_hour":       pickup_hour,
                "pickup_dow":        pickup_dow,
                "period_type":       period,
                "is_intra_borough":  bool(is_intra_borough),
                "is_airport":        bool(is_airport),
            },
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error("Duration prediction error: %s", e)
        return {"success": False, "error": f"Prediction failed: {e}"}


# ─── 3. Demand Forecasting ────────────────────────────────────────────────────

def forecast_demand(
    zone_name: str,
    target_date: str,   # YYYY-MM-DD
    target_hour: int,
) -> dict:
    """
    Forecast pickup demand (trips/hour) for a zone at a specific date+hour.
    Computes required lag features from historical Parquet data.
    """
    try:
        zone = _zone_row(zone_name)
        loc_id = int(zone["loc_id"])

        # Compute lag features via DuckDB
        lag_query = f"""
        WITH hourly AS (
            SELECT
                DATE_TRUNC('hour', pickup_timestamp)  AS hour_ts,
                COUNT(*) AS trips
            FROM read_parquet('{PARQUET_FILE}')
            WHERE origin_loc_id = {loc_id}
            GROUP BY hour_ts
        )
        SELECT
            COALESCE((SELECT trips FROM hourly WHERE hour_ts = TIMESTAMP '{target_date} {target_hour:02d}:00:00' - INTERVAL 24 HOUR),  0) AS lag_24h,
            COALESCE((SELECT trips FROM hourly WHERE hour_ts = TIMESTAMP '{target_date} {target_hour:02d}:00:00' - INTERVAL 48 HOUR),  0) AS lag_48h,
            COALESCE((SELECT trips FROM hourly WHERE hour_ts = TIMESTAMP '{target_date} {target_hour:02d}:00:00' - INTERVAL 72 HOUR),  0) AS lag_72h,
            COALESCE((SELECT trips FROM hourly WHERE hour_ts = TIMESTAMP '{target_date} {target_hour:02d}:00:00' - INTERVAL 168 HOUR), 0) AS lag_168h,
            COALESCE((
                SELECT AVG(trips) FROM hourly
                WHERE hour_ts >= TIMESTAMP '{target_date} {target_hour:02d}:00:00' - INTERVAL 24 HOUR
                  AND hour_ts <  TIMESTAMP '{target_date} {target_hour:02d}:00:00'
            ), 0) AS rolling_mean_24h
        """

        stats = duckdb.query(lag_query).df().iloc[0]

        lag_24h       = float(stats["lag_24h"])
        lag_48h       = float(stats["lag_48h"])
        lag_72h       = float(stats["lag_72h"])
        lag_168h      = float(stats["lag_168h"])
        rolling_mean  = float(stats["rolling_mean_24h"])

        if lag_24h == 0 and lag_48h == 0 and lag_72h == 0 and lag_168h == 0:
            return {
                "success": False,
                "error": (
                    f"Insufficient historical data for zone '{zone_name}' "
                    f"around {target_date} {target_hour:02d}:00. "
                    "The model requires prior hourly trip counts for this zone."
                ),
            }

        features = pd.DataFrame([{
            "lag_24h":        lag_24h,
            "lag_48h":        lag_48h,
            "lag_72h":        lag_72h,
            "lag_168h":       lag_168h,
            "rolling_mean_24h": rolling_mean,
        }])

        model = _get_demand_model()
        # Try to predict — model may have different feature names; handle gracefully
        try:
            predicted = float(model.predict(features)[0])
        except Exception:
            # Try column name variants from notebook
            features.columns = ["lag_24h", "lag_48h", "lag_72h", "lag_168h", "rolling_24h"]
            predicted = float(model.predict(features)[0])

        predicted = max(0, round(predicted))

        return {
            "success":           True,
            "zone_name":         zone_name,
            "target_date":       target_date,
            "target_hour":       target_hour,
            "predicted_pickups": predicted,
            "lag_features": {
                "lag_24h":        lag_24h,
                "lag_48h":        lag_48h,
                "lag_72h":        lag_72h,
                "lag_168h":       lag_168h,
                "rolling_mean_24h": rolling_mean,
            },
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error("Demand forecasting error: %s", e)
        return {"success": False, "error": f"Forecast failed: {e}"}


# ─── 4. Zone Clustering ────────────────────────────────────────────────────────

def classify_zone(zone_name: str) -> dict:
    """
    Classify a zone into its K-Means demand-pattern cluster.
    Uses the 24-hour diurnal demand profile computed from Parquet.
    """
    try:
        zone = _zone_row(zone_name)
        loc_id = int(zone["loc_id"])

        # Build 24-hour demand profile
        profile_query = f"""
        SELECT
            CAST(EXTRACT(hour FROM pickup_timestamp) AS INTEGER) AS hr,
            COUNT(*) AS trips
        FROM read_parquet('{PARQUET_FILE}')
        WHERE origin_loc_id = {loc_id}
        GROUP BY hr
        ORDER BY hr
        """
        df = duckdb.query(profile_query).df()

        # Build full 24-element profile (fill missing hours with 0)
        profile = np.zeros(24)
        for _, row in df.iterrows():
            hr = int(row["hr"])
            if 0 <= hr <= 23:
                profile[hr] = float(row["trips"])

        if profile.sum() == 0:
            return {
                "success": False,
                "error": f"No historical trip data found for zone '{zone_name}'.",
            }

        model = _get_cluster_model()
        cluster_id = int(model.predict([profile])[0])
        cluster_label = CLUSTER_LABELS.get(cluster_id, f"Cluster {cluster_id}")

        return {
            "success":       True,
            "zone_name":     zone_name,
            "cluster_id":    cluster_id,
            "cluster_label": cluster_label,
            "description":   _cluster_description(cluster_id),
            "demand_profile_24h": profile.tolist(),
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error("Zone clustering error: %s", e)
        return {"success": False, "error": f"Clustering failed: {e}"}


def _cluster_description(cluster_id: int) -> str:
    desc = {
        0: (
            "This zone exhibits a strong morning commuter pattern with peak demand "
            "during AM rush hours (7–9 AM), typical of transit hubs and business "
            "district entry points."
        ),
        1: (
            "This zone has sustained high demand throughout the daytime (9 AM–5 PM), "
            "characteristic of commercial districts, shopping areas, and office parks."
        ),
        2: (
            "This zone peaks during evening and nighttime hours, typical of dining, "
            "entertainment, and nightlife destinations popular after 6 PM."
        ),
        3: (
            "This zone shows consistently low or dispersed demand across all hours, "
            "typical of residential suburbs or peripheral areas with irregular taxi usage."
        ),
    }
    return desc.get(cluster_id, "Demand pattern not specifically documented.")
