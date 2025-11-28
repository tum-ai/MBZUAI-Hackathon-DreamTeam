import asyncio
import json
from typing import Dict, Any

from llm.editor.models import EditRequest
from llm.editor.editor import process_edit_request
from llm.actor.models import ActionRequest
from llm.actor.actor import process_action_request
from llm.clarifier.models import ClarifyRequest
from llm.clarifier.clarifier import process_clarification_request

async def edit_tool(session_id: str, step_id: str, intent: str, context: str) -> str:
    """
    Wraps the existing editor agent.
    """
    print(f"   [TOOL RUNNING] Edit Tool: {intent}")
    request = EditRequest(
        session_id=session_id,
        step_id=step_id,
        intent=intent,
        context=context
    )
    try:
        response = await process_edit_request(request)
        return f"Success: Generated code patch: {response.code}"
    except Exception as e:
        return f"Error in Edit Tool: {str(e)}"

async def action_tool(session_id: str, step_id: str, intent: str, context: str) -> str:
    """
    Wraps the existing actor agent.
    """
    print(f"   [TOOL RUNNING] Action Tool: {intent}")
    request = ActionRequest(
        session_id=session_id,
        step_id=step_id,
        intent=intent,
        context=context
    )
    try:
        response = await process_action_request(request)
        # Return just the action JSON for frontend consumption
        return response.action
    except Exception as e:
        return f"Error in Action Tool: {str(e)}"

async def clarify_tool(session_id: str, step_id: str, intent: str, context: str) -> str:
    """
    Wraps the existing clarifier agent.
    """
    print(f"   [TOOL RUNNING] Clarify Tool: {intent}")
    request = ClarifyRequest(
        session_id=session_id,
        step_id=step_id,
        intent=intent,
        context=context
    )
    try:
        response = await process_clarification_request(request)
        return f"Success: Generated clarification: {response.reply}"
    except Exception as e:
        return f"Error in Clarify Tool: {str(e)}"

# Map string names to functions
TOOL_MAP = {
    "edit_tool": edit_tool,
    "action_tool": action_tool,
    "clarify_tool": clarify_tool
}
