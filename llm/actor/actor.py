import logging
import sys
from pathlib import Path

from .models import ActionRequest, ActionResponse
from .llm_client import generate_action

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planner.session_manager import load_session, save_session

logger = logging.getLogger(__name__)


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

    dom_snapshot = {}
    try:
        snapshot_response = await server_module.fetch_dom_snapshot()
        dom_snapshot = (
            snapshot_response.get("snapshot", {}) if snapshot_response else {}
        )
    except Exception as exc:
        logger.warning(
            "Failed to fetch DOM snapshot for session %s step %s: %s",
            request.session_id,
            request.step_id,
            exc,
        )

    system_prompt = server_module.get_system_prompt(dom_snapshot)

    action = generate_action(
        intent=request.intent,
        context=request.context,
        system_prompt=system_prompt,
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

    response = ActionResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        action=action,
    )

    return response
