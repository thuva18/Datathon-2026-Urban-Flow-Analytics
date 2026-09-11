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
- DATA_QUERY: Historical questions (e.g. "How many trips yesterday?", "Average fare in Manhattan"). If it's a DATA_QUERY, generate a safe DuckDB SQL query in the 'sql_query' parameter using this schema:
{get_schema_description()}
- FARE_PREDICTION: Forecasting future fare cost for a trip between origin and destination.
- DURATION_PREDICTION: Forecasting trip time/length between origin and destination.
- DEMAND_FORECAST: Predicting future pickup volume for a specific zone.
- ZONE_CLUSTERING: Identifying the behavioral cluster/type of a taxi zone.
- RAG_KNOWLEDGE: Questions about the project, methodology, or dataset documentation.
- COMBINED_QUERY: Questions requiring multiple tools (e.g. "highest demand tomorrow AND trips last month").
- CASUAL_GREETING: Conversational greetings, "hello", "hi", "how are you".
- UNSUPPORTED_QUERY: Questions unrelated to taxi data explicitly.

PARAMETERS TO EXTRACT (if present):
- origin_zone: The pickup location
- dest_zone: The dropoff location
- target_zone: A single location for demand/clustering
- date: Mentioned date (e.g. "tomorrow", "2026-09-12")
- time: Mentioned time (e.g. "8 AM", "evening rush")
- sql_query: If intent=DATA_QUERY or COMBINED_QUERY, provide the exact safe DuckDB SQL query. Only SELECT statements are allowed. Add LIMIT 500.

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

If a required parameter is missing, set needs_clarification=true and list it in missing_parameters.
"""

def extract_intent(user_message: str) -> dict:
    """Call Groq to extract intent. Returns structured dict or error."""
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        return {"success": False, "error": "GROQ_API_KEY is not set."}

    client = Groq(api_key=GROQ_API_KEY)
    # Try the selected model first, then fall through the preference list
    model_order = [GROQ_MODEL] + [m for m in GROQ_MODEL_PREFERENCE if m != GROQ_MODEL]

    for model in model_order:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            content = response.choices[0].message.content
            result = json.loads(content)
            result["success"] = True
            if model != GROQ_MODEL:
                logger.warning(f"Intent extraction used fallback model: {model}")
            return result
        except json.JSONDecodeError:
            logger.error("Groq returned invalid JSON during intent extraction.")
            return {"success": False, "error": "Model returned invalid format."}
        except Exception as exc:
            logger.warning(f"Intent extraction model {model!r} failed: {exc}")

    return {"success": False, "error": "All Groq models failed for intent extraction."}
