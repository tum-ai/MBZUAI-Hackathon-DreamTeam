import logging
import sys
import os
import json
import asyncio
from pathlib import Path
import websockets

from .models import ActionRequest, ActionResponse
from .llm_client import generate_action

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planner.session_manager import load_session, save_session

logger = logging.getLogger(__name__)

# Configuration for DOM WebSocket (same as in llm/server.py)
DOM_SNAPSHOT_WS_URL = os.getenv("DOM_SNAPSHOT_WS_URL", "ws://localhost:5173/dom-snapshot")


def _preview(text: str, *, length: int = 160) -> str:
    if not text:
        return ""
    condensed = " ".join(text.split())
    if len(condensed) <= length:
        return condensed
    return f"{condensed[:length]}..."


async def process_action_request(request: ActionRequest) -> ActionResponse:
    """
    Process action request through the actor agent.

    Steps:
    1. Pull the dom snapshot from the executor server
    2. Generate action using LLM with the dom snapshot and the intent and context
    2. Save action to session with step_id
    3. Return complete response with action
    """
    from llm import server as server_module

    truncated_intent = _preview(request.intent)
    truncated_context = _preview(request.context)
    logger.info(
        "Actor request received: session=%s step=%s intent='%s' context='%s'",
        request.session_id,
        request.step_id,
        truncated_intent,
        truncated_context,
    )

    dom_snapshot = {}
    try:
        snapshot_response = await server_module.fetch_dom_snapshot()
        dom_snapshot = (
            snapshot_response.get("snapshot", {}) if snapshot_response else {}
        )
        logger.info(
            "Actor DOM snapshot fetched: session=%s step=%s elements=%s iframeElements=%s",
            request.session_id,
            request.step_id,
            len(dom_snapshot.get("elements", [])),
            dom_snapshot.get("iframeElementCount"),
        )
    except Exception as exc:
        logger.warning(
            "Failed to fetch DOM snapshot for session %s step %s: %s",
            request.session_id,
            request.step_id,
            exc,
        )

    system_prompt = server_module.get_system_prompt(dom_snapshot)

    logger.info(
        "Actor generating action: session=%s step=%s systemPromptChars=%s",
        request.session_id,
        request.step_id,
        len(system_prompt) if system_prompt else 0,
    )

    action = generate_action(
        intent=request.intent,
        context=request.context,
        system_prompt=system_prompt,
    )

    logger.info(
        "Actor generated action: session=%s step=%s action='%s'",
        request.session_id,
        request.step_id,
        _preview(action, length=200),
    )

    session = load_session(request.session_id)

    if "actions" not in session:
        session["actions"] = {}

    session["actions"][request.step_id] = {
        "intent": request.intent,
        "context": request.context,
        "action": action,
    }

    save_session(request.session_id, session)

    # Send action to frontend via WebSocket
    automation_status = await send_action_to_frontend(action)

    response = ActionResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        action=action,
        automation_status=automation_status,
    )

    logger.info(
        "Actor response returning: session=%s step=%s actionLength=%s",
        response.session_id,
        response.step_id,
        len(response.action) if response.action else 0,
    )

    return response


async def send_action_to_frontend(action_string: str) -> str:
    """
    Send the generated action to the frontend via WebSocket for execution.
    
    The frontend is already connected to the DOM snapshot WebSocket bridge.
    We send a message with type='browser_action' containing the parsed action.
    
    Args:
        action_string: The action string from LLM (e.g., "click(targetId='button-1')")
        
    Returns:
        Status message about the action broadcast
    """
    try:
        # Parse the action string into browser action format
        browser_action = parse_action_string(action_string)
        
        logger.info(f"Sending action to frontend via WebSocket: {browser_action}")
        
        # Connect to the DOM snapshot WebSocket and broadcast the action
        async with websockets.connect(DOM_SNAPSHOT_WS_URL, ping_interval=None) as websocket:
            # Register as backend
            await websocket.send(json.dumps({"type": "register", "role": "backend"}))
            
            # Send browser action message
            action_message = {
                "type": "browser_action",
                "action": browser_action,
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(action_message))
            
            logger.info(f"Action broadcast successfully: {browser_action.get('action')}")
            return f"Action sent to frontend: {browser_action.get('action')} on {browser_action.get('targetId', 'N/A')}"
                
    except (websockets.exceptions.WebSocketException, ConnectionError) as e:
        error_msg = f"Failed to connect to DOM WebSocket: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error sending action to frontend: {str(e)}"
        logger.error(error_msg)
        return error_msg


def parse_action_string(action_string: str) -> dict:
    """
    Parse LLM-generated action string into BrowserAction format.
    
    Examples:
        "click(targetId='contact-button')" → {"action": "click", "targetId": "contact-button"}
        "scroll(direction='down', amount=500)" → {"action": "scroll", "direction": "down", "amount": 500}
        "type(targetId='search-box', text='hello')" → {"action": "type", "targetId": "search-box", "text": "hello"}
    """
    import re
    import json
    
    # Try to parse as JSON first
    try:
        if action_string.strip().startswith("{"):
            return json.loads(action_string.strip())
    except json.JSONDecodeError:
        pass
    
    # Extract action name
    action_match = re.match(r"(\w+)\((.*)\)", action_string.strip())
    if not action_match:
        # Fallback: treat entire string as action type
        return {"action": action_string.strip()}
    
    action_type = action_match.group(1)
    params_str = action_match.group(2)
    
    # Parse parameters
    params = {"action": action_type}
    
    # Match key='value' or key=123 patterns
    param_pattern = r"(\w+)=(?:'([^']*)'|(\d+))"
    for match in re.finditer(param_pattern, params_str):
        key = match.group(1)
        value = match.group(2) if match.group(2) is not None else int(match.group(3))
        params[key] = value
    
    return params
