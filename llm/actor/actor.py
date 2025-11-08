from .models import ActionRequest, ActionResponse
from .llm_client import generate_action
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planner.session_manager import load_session, save_session


def process_action_request(request: ActionRequest) -> ActionResponse:
    """
    Process action request through the actor agent.

    Steps:
    1. Generate action using LLM
    2. Save action to session with step_id
    3. Return complete response with action
    """
    action = generate_action(request.intent, request.context)

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
