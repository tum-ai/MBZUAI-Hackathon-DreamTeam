import logging
import sys
from pathlib import Path

from .models import ActionRequest, ActionResponse
from .llm_client import generate_action

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planner.session_manager import load_session, save_session

logger = logging.getLogger(__name__)


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

    logger.info(
        "Actor response stored: session=%s step=%s historyCount=%s",
        request.session_id,
        request.step_id,
        len(session.get("actions", {})),
    )

    response = ActionResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        action=action,
    )

    logger.info(
        "Actor response returning: session=%s step=%s actionLength=%s",
        response.session_id,
        response.step_id,
        len(response.action) if response.action else 0,
    )

    return response
