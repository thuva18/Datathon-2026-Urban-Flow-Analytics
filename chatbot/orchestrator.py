"""
chatbot/orchestrator.py
Main entry point for chatbot logic.
Streamlit calls `process_message(user_message)` which ties everything together.
"""
import logging
from chatbot import intent_extractor
from chatbot import intent_router
from chatbot import response_generator

logger = logging.getLogger("chatbot")

def process_message(user_message: str) -> dict:
    """
    1. Extract Intent
    2. Check Clarification
    3. Route to Tool
    4. Generate Final Response
    
    Returns standard interface:
    {
       "answer": "Text response",
       "intent": "INTENT",
       "tool_used": "Tool Name",
       "data": {...raw tool output...},
       "metadata": {}
    }
    """
    logger.info(f"Processing message: {user_message}")
    
    # 1. Extraction
    extraction = intent_extractor.extract_intent(user_message)
    if not extraction.get("success"):
        return {
            "answer": f"I hit an error trying to understand your request: {extraction.get('error')}",
            "intent": "ERROR",
            "tool_used": "None",
            "data": {},
            "metadata": {}
        }
        
    # 2. Need Clarification?
    if extraction.get("needs_clarification"):
        missing = ", ".join(extraction.get("missing_parameters", []))
        return {
            "answer": f"To help with that, could you please provide: {missing}?",
            "intent": "CLARIFICATION_REQUIRED",
            "tool_used": "None",
            "data": {},
            "metadata": {}
        }
        
    # 3. Route
    print(extraction)
    tool_result = intent_router.route(extraction, user_message)
    tool_used = tool_result.get("tool_used", "None")
    
    # 4. Generate NL Response
    answer = response_generator.generate_response(user_message, tool_result)
    
    return {
        "answer": answer,
        "intent": tool_result.get("intent", extraction.get("intent")),
        "tool_used": tool_used,
        "data": tool_result,
        "metadata": {
            "sql_used": tool_result.get("sql_used")
        }
    }
