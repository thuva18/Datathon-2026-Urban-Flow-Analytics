"""
tests/test_chatbot.py
Comprehensive automated tests for chatbot routing and tools.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import backend modules
from chatbot import sql_service
from chatbot import model_services
from chatbot import rag_service
from chatbot import intent_router
from chatbot import parameter_resolver

# ─── Mocked Data ─────────────────────────────────────────────────────────────

def mock_get_zones():
    import pandas as pd
    return pd.DataFrame([
        {"loc_id": 132, "borough_name": "Queens", "zone_name": "JFK Airport", "service_zone": "Airports"},
        {"loc_id": 230, "borough_name": "Manhattan", "zone_name": "Times Sq/Theatre District", "service_zone": "Yellow Zone"},
        {"loc_id": 1, "borough_name": "EWR", "zone_name": "Newark Airport", "service_zone": "EWR"},
    ])

# ─── 1. SQL Service Tests ────────────────────────────────────────────────────

def test_sql_validation_safe():
    safe_sql = "SELECT COUNT(*) FROM read_parquet('test.parquet')"
    is_safe, msg = sql_service.validate_sql(safe_sql)
    assert is_safe

def test_sql_validation_unsafe():
    unsafe_sql = "DROP TABLE my_table;"
    is_safe, msg = sql_service.validate_sql(unsafe_sql)
    assert not is_safe
    assert "forbidden" in msg.lower()
    
def test_sql_validation_insert():
    unsafe_sql = "INSERT INTO test VALUES (1);"
    is_safe, msg = sql_service.validate_sql(unsafe_sql)
    assert not is_safe

def test_sql_limit_enforcement():
    sql = "SELECT * FROM dataset"
    enforced = sql_service.enforce_limit(sql)
    assert "LIMIT 500" in enforced

# ─── 2. Parameter Resolution Tests ──────────────────────────────────────────

@patch("chatbot.parameter_resolver._get_zone_names")
def test_zone_resolution(mock_names):
    mock_names.return_value = ["JFK Airport", "Times Sq/Theatre District", "Astoria"]
    
    assert parameter_resolver.resolve_zone("JFK") == "JFK Airport"
    assert parameter_resolver.resolve_zone("Times Square") == "Times Sq/Theatre District"
    assert parameter_resolver.resolve_zone("Fake Zone XYZ") is None

def test_time_resolution():
    assert parameter_resolver.resolve_hour("8 AM") == 8
    assert parameter_resolver.resolve_hour("8 pm") == 20
    assert parameter_resolver.resolve_hour("18:30") == 18
    assert parameter_resolver.resolve_hour("evening rush") == 17

def test_date_resolution():
    # Relative checks against fixed SYSTEM_DATE = 2026-09-12
    assert parameter_resolver.resolve_date("yesterday") == "2026-09-11"
    assert parameter_resolver.resolve_date("today") == "2026-09-12"
    assert parameter_resolver.resolve_date("tomorrow") == "2026-09-13"

# ─── 3. Intent Router Tests ────────────────────────────────────────────────

@patch("chatbot.model_services.predict_fare")
@patch("chatbot.parameter_resolver.resolve_zone")
def test_router_fare(mock_resolve, mock_predict):
    mock_resolve.side_effect = lambda x: "JFK Airport" if "jfk" in x.lower() else "Times Sq"
    mock_predict.return_value = {"success": True, "predicted_fare": 55.4}
    
    intent_data = {
        "intent": "FARE_PREDICTION",
        "parameters": {"origin_zone": "JFK", "dest_zone": "Times Square", "time": "6 PM"}
    }
    
    res = intent_router.route(intent_data, "how much from JFK to Times Sq at 6 PM?")
    assert res["success"]
    assert res["tool_used"] == "Fare Model"
    mock_predict.assert_called_once()

@patch("chatbot.model_services.forecast_demand")
@patch("chatbot.parameter_resolver.resolve_zone")
def test_router_demand(mock_resolve, mock_predict):
    mock_resolve.return_value = "JFK Airport"
    mock_predict.return_value = {"success": True, "predicted_pickups": 500}
    
    intent_data = {
        "intent": "DEMAND_FORECAST",
        "parameters": {"target_zone": "JFK", "time": "8 AM", "date": "tomorrow"}
    }
    
    res = intent_router.route(intent_data, "demand at JFK tomorrow at 8 AM")
    assert res["success"]
    assert res["tool_used"] == "Demand Model"

def test_router_unsupported():
    intent_data = {"intent": "UNSUPPORTED_QUERY"}
    res = intent_router.route(intent_data, "tell me a poem about cooking recipes")
    assert not res["success"]
    assert "outside the scope" in res["error"]

def test_rag_retrieval_success():
    res = rag_service.retrieve_knowledge("traffic speed drop Manhattan rush hour")
    assert res["success"]
    assert len(res["chunks"]) > 0

def test_router_greeting():
    intent_data = {"intent": "CASUAL_GREETING"}
    res = intent_router.route(intent_data, "hello")
    assert res["success"]
    assert res["intent"] == "CASUAL_GREETING"

@patch("chatbot.model_services.predict_fare")
def test_router_sample_fare_fallback(mock_predict):
    mock_predict.return_value = {"success": True, "predicted_fare": 71.51}
    intent_data = {
        "intent": "FARE_PREDICTION",
        "parameters": {}  # empty parameters -> auto-defaults to JFK and Times Sq
    }
    res = intent_router.route(intent_data, "use some sample ones")
    assert res["success"]
    assert res["tool_used"] == "Fare Model"
    mock_predict.assert_called_once()
