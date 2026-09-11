"""
chatbot/intent_extractor.py
Uses Groq to classify the user's message into an intent and extract parameters.
"""
import os
import json
import logging
from groq import Groq
from chatbot.config import GROQ_API_KEY, GROQ_MODEL, GROQ_MODEL_PREFERENCE
from chatbot.sql_service import get_schema_description

logger = logging.getLogger("chatbot")

# Intent definitions
INTENTS = [
    "DATA_QUERY", 
    "FARE_PREDICTION", 
    "DURATION_PREDICTION", 
    "DEMAND_FORECAST", 
    "ZONE_CLUSTERING", 
    "RAG_KNOWLEDGE", 
    "COMBINED_QUERY", 
    "CASUAL_GREETING",
    "UNSUPPORTED_QUERY"

]

SYSTEM_PROMPT = f"""You are the intent extraction engine for the Urban Flow Analytics taxi chatbot.
Your job is to classify the user's question into one of the exact intents and extract any parameters mentioned.

AVAILABLE INTENTS:
- DATA_QUERY: Historical aggregate queries (e.g. "Total rides in Manhattan", "Busiest pickup day", "Average fare").
  If DATA_QUERY, generate a safe DuckDB SQL query in the 'sql_query' parameter using this schema:
{get_schema_description()}
  CRITICAL SQL RULES:
  * The dataset spans 2025-04-01 to 2026-03-31 (48,601,782 records).
  * NEVER use CURRENT_TIMESTAMP, CURRENT_DATE, or NOW() in SQL queries!
  * If the user asks about "right now", "today", "yesterday", or current traffic conditions, do NOT query current system dates. Instead query by hour of day (EXTRACT(hour FROM pickup_timestamp)) and day of week (EXTRACT(dow FROM pickup_timestamp)), OR if asking about traffic congestion in Manhattan, classify as RAG_KNOWLEDGE.
- FARE_PREDICTION: Forecasting future fare cost for a trip between origin and destination.
- DURATION_PREDICTION: Forecasting trip time/length between origin and destination.
- DEMAND_FORECAST: Predicting future pickup volume for a specific zone.
- ZONE_CLUSTERING: Identifying the behavioral cluster/type of a taxi zone.
- RAG_KNOWLEDGE: Questions about the project, methodology, dataset documentation, findings, traffic speeds, congestion patterns, anomalies, or general overview ("tell me about taxi data", "traffic in Manhattan", "tell me about other things", "what else").
- COMBINED_QUERY: Questions requiring multiple tools.
- CASUAL_GREETING: Conversational greetings, "hello", "hi", "how are you", "what can you do", "help".
- UNSUPPORTED_QUERY: Only strictly unrelated non-mobility questions (e.g. recipes, sports, poetry). If user asks conversational prompts ("nk", "ok tell", "more", "tell me about other things"), classify as RAG_KNOWLEDGE or CASUAL_GREETING.

PARAMETERS TO EXTRACT (if present):
- origin_zone: The pickup location
- dest_zone: The dropoff location
- target_zone: A single location for demand/clustering
- date: Mentioned date (e.g. "tomorrow", "2026-09-12")
- time: Mentioned time (e.g. "8 AM", "evening rush")
- sql_query: If intent=DATA_QUERY or COMBINED_QUERY, provide the exact safe DuckDB SQL query. Only SELECT statements are allowed. Add LIMIT 500.

SAMPLE & DEFAULT PREDICTIONS:
If the user asks to predict without specifying locations (e.g. "can you predict", "predict something", "use some sample ones", "give an example", "get from our prediction data"), supply default sample parameters:
- origin_zone: "JFK Airport"
- dest_zone: "Times Square"
- time: "18:00"
- needs_clarification: false

IMPORTANT: Output your response as a valid JSON object matching this schema EXACTLY:
{{
  "intent": "<ONE_OF_THE_INTENTS>",
  "parameters": {{
    "origin_zone": "extracted or null",
    "dest_zone": "extracted or null",
    "target_zone": "extracted or null",
    "date": "extracted or null",
    "time": "extracted or null",
    "sql_query": "extracted or null"
  }},
  "missing_parameters": ["list", "of", "missing", "required", "params"],
  "needs_clarification": true/false
}}

REQUIRED PARAMS BY INTENT:
FARE_PREDICTION requires origin_zone, dest_zone, time.
DURATION_PREDICTION requires origin_zone, dest_zone.
DEMAND_FORECAST requires target_zone, date, time.
ZONE_CLUSTERING requires target_zone.

If a required parameter is missing AND the user has not asked for samples/examples, set needs_clarification=true and list it in missing_parameters.
If needs_clarification is true, missing_parameters MUST NOT be empty.
"""

def extract_intent(user_message: str, history: list[dict] = None) -> dict:
    """Call Groq to extract intent with optional multi-turn conversation history."""
    # Fast heuristic check for casual greetings or broad filler
    clean_msg = user_message.strip().lower()
    if clean_msg in ["hi", "hello", "hey", "help", "what can you do", "nk", "ok", "ok tell", "tell me"]:
        return {
            "intent": "CASUAL_GREETING",
            "parameters": {
                "origin_zone": None, "dest_zone": None, "target_zone": None,
                "date": None, "time": None, "sql_query": None
            },
            "missing_parameters": [],
            "needs_clarification": False,
            "success": True
        }

    # Heuristic check for sample prediction request
    if any(phrase in clean_msg for phrase in ["sample", "example", "default", "prediction data", "cant u predict", "can you predict"]):
        if not ("who" in clean_msg or "how does" in clean_msg or "what is" in clean_msg):
            return {
                "intent": "FARE_PREDICTION",
                "parameters": {
                    "origin_zone": "JFK Airport",
                    "dest_zone": "Times Square",
                    "target_zone": None,
                    "date": "2026-09-12",
                    "time": "18:00",
                    "sql_query": None
                },
                "missing_parameters": [],
                "needs_clarification": False,
                "success": True
            }

    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        return {"success": False, "error": "GROQ_API_KEY is not set."}

    client = Groq(api_key=GROQ_API_KEY, max_retries=0)
    model_order = [GROQ_MODEL] + [m for m in GROQ_MODEL_PREFERENCE if m != GROQ_MODEL]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history[-4:]:
            role = "assistant" if msg.get("role") == "assistant" else "user"
            content = msg.get("content", "")
            if content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    for model in model_order:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.0
            )
            content = response.choices[0].message.content
            result = json.loads(content)
            result["success"] = True
            
            # Guard against needs_clarification=True with empty missing_parameters
            if result.get("needs_clarification") and not result.get("missing_parameters"):
                result["needs_clarification"] = False
                
            if model != GROQ_MODEL:
                logger.warning(f"Intent extraction used fallback model: {model}")
            return result
        except json.JSONDecodeError:
            logger.error("Groq returned invalid JSON during intent extraction.")
            return {"success": False, "error": "Model returned invalid format."}
        except Exception as exc:
            logger.warning(f"Intent extraction model {model!r} failed: {exc}")

    return {"success": False, "error": "All Groq models failed for intent extraction."}
