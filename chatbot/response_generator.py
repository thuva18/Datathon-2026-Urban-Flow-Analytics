"""
chatbot/response_generator.py
Uses Groq to format tool output into a clean, concise natural-language response.
"""
import os
import json
import logging
from groq import Groq
from chatbot.config import GROQ_API_KEY, GROQ_MODEL, GROQ_MODEL_PREFERENCE

logger = logging.getLogger("chatbot")

# Build the runtime fallback list: start from whichever model was selected at
# startup, then continue with the rest so we never retry an already-failed one.
_RUNTIME_ORDER = (
    [GROQ_MODEL] +
    [m for m in GROQ_MODEL_PREFERENCE if m != GROQ_MODEL]
)

def generate_response(original_query: str, tool_result: dict) -> str:
    """Takes the exact data from the DB/models and generates a plain English response."""
    
    if tool_result.get("intent") == "CASUAL_GREETING":
        return "Hello! I am the Urban Flow Analytics AI assistant. I can query our 48M+ row taxi dataset, forecast demand, and predict fares. How can I help you today?"

    if not tool_result.get("success"):
        error = tool_result.get("error", "Unknown error")
        
        # If it's merely an unsupported query, we can just say that cleanly.
        if tool_result.get("intent") == "UNSUPPORTED_QUERY":
            return "I can only answer questions related to taxi data, modeling, and analytics."
            
        return f"I couldn't complete that request because: {error}"
        
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Fallback to returning raw JSON if no API key is present
        return f"Query successful. Raw results: {json.dumps(tool_result, default=str)}"
        
    system_prompt = f"""You are the response generation engine for the Urban Flow Analytics chatbot.
The user asked a question. A backend tool (SQL, ML model, or RAG) was executed safely and produced the following JSON result:

{json.dumps(tool_result, default=str)}

Your job is to read this JSON result and answer the user's question accurately in natural language.
RULES:
1. Do NOT hallucinate or change numbers.
2. If it's a model prediction, state the prediction clearly.
3. If it's a SQL result, summarize the data directly. Give the exact numbers.
4. If it's RAG, synthesize the chunks into a clear answer.
5. Keep it concise, friendly, and professional. 
6. Do NOT mention "JSON", "backend tool", "DuckDB", or "SQL" in your answer unless the user asked about it. Just report the data."""

    t_result_len = len(json.dumps(tool_result, default=str))
    if t_result_len > 10000:
        # If SQL pulled too much, truncate
        tool_result["data"] = tool_result["data"][:10]
        # Rewrite system prompt with shortened payload
        system_prompt = f"""You are the response generation engine for the Urban Flow Analytics chatbot.
The user asked a question. A backend tool was executed safely and produced the following JSON result (truncated to top 10):

{json.dumps(tool_result, default=str)}

Your job is to read this JSON result and answer the user's question accurately in natural language."""

    client = Groq(api_key=GROQ_API_KEY)
    last_exc = None
    for model in _RUNTIME_ORDER:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": original_query}
                ],
                temperature=0.3
            )
            if model != GROQ_MODEL:
                logger.warning(f"Primary model unavailable; used fallback: {model}")
            return response.choices[0].message.content
        except Exception as exc:
            logger.warning(f"Model {model!r} failed: {exc}")
            last_exc = exc

    logger.error(f"All Groq models failed. Last error: {last_exc}")
    return f"Query successful. Raw results: {json.dumps(tool_result, default=str)}"
