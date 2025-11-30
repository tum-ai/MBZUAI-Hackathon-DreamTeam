import asyncio
import json
import logging
from typing import Dict, Any

# Import new Langchain-based agents
from llm_new.actor_agent import generate_action_llm
from llm_new.editor_agent import generate_code_llm
from llm_new.clarifier_agent import generate_clarification_llm

logger = logging.getLogger(__name__)

async def edit_tool(session_id: str, step_id: str, intent: str, context: str) -> str:
    """
    Wraps the new editor agent using Langchain.
    """
    print(f"   [TOOL RUNNING] Edit Tool: {intent}")
    logger.info(f"[EDIT_TOOL] Input - session_id: {session_id}, step_id: {step_id}")
    logger.info(f"[EDIT_TOOL] Intent: {intent}")
    logger.info(f"[EDIT_TOOL] Context: {context}")
    
    try:
        code_json = await generate_code_llm(intent, context)
        logger.info(f"[EDIT_TOOL] Output length: {len(code_json)}")
        logger.info(f"[EDIT_TOOL] Output (first 200 chars): {code_json[:200]}")
        return code_json
    except Exception as e:
        logger.error(f"[EDIT_TOOL] Error: {str(e)}")
        import traceback
        logger.error(f"[EDIT_TOOL] Traceback: {traceback.format_exc()}")
        return f"Error in Edit Tool: {str(e)}"

async def action_tool(session_id: str, step_id: str, intent: str, context: str) -> str:
    """
    Wraps the new actor agent using Langchain.
    """
    print(f"   [TOOL RUNNING] Action Tool: {intent}")
    logger.info(f"[ACTION_TOOL] Input - session_id: {session_id}, step_id: {step_id}")
    logger.info(f"[ACTION_TOOL] Intent: {intent}")
    logger.info(f"[ACTION_TOOL] Context: {context}")
    
    try:
        action_json = await generate_action_llm(intent, context, session_id, step_id)
        logger.info(f"[ACTION_TOOL] Output length: {len(action_json)}")
        logger.info(f"[ACTION_TOOL] Output (first 200 chars): {action_json[:200]}")
        # Return just the action JSON for frontend consumption
        return action_json
    except Exception as e:
        logger.error(f"[ACTION_TOOL] Error: {str(e)}")
        import traceback
        logger.error(f"[ACTION_TOOL] Traceback: {traceback.format_exc()}")
        return f"Error in Action Tool: {str(e)}"

async def clarify_tool(session_id: str, step_id: str, intent: str, context: str) -> str:
    """
    Wraps the new clarifier agent using Langchain.
    """
    print(f"   [TOOL RUNNING] Clarify Tool: {intent}")
    logger.info(f"[CLARIFY_TOOL] Input - session_id: {session_id}, step_id: {step_id}")
    logger.info(f"[CLARIFY_TOOL] Intent: {intent}")
    logger.info(f"[CLARIFY_TOOL] Context: {context}")
    
    try:
        clarification = await generate_clarification_llm(intent, context)
        logger.info(f"[CLARIFY_TOOL] Output: {clarification}")
        return clarification
    except Exception as e:
        logger.error(f"[CLARIFY_TOOL] Error: {str(e)}")
        import traceback
        logger.error(f"[CLARIFY_TOOL] Traceback: {traceback.format_exc()}")
        return f"Error in Clarify Tool: {str(e)}"

# Map string names to functions
TOOL_MAP = {
    "edit_tool": edit_tool,
    "action_tool": action_tool,
    "clarify_tool": clarify_tool
}
