from .models import ClarifyRequest, ClarifyResponse
from .llm_client import generate_clarification
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planner.session_manager import load_session, save_session


def process_clarification_request(request: ClarifyRequest) -> ClarifyResponse:
    """
    Process clarification request through the Jarvis-style clarifier agent.
    
    Steps:
    1. Generate clarification reply using LLM with Jarvis personality
    2. Save clarification to session with step_id
    3. Return complete response with reply
    """
    reply = generate_clarification(request.intent, request.context)
    
    session = load_session(request.session_id)
    
    if "clarifications" not in session:
        session["clarifications"] = {}
    
    session["clarifications"][request.step_id] = {
        "intent": request.intent,
        "context": request.context,
        "reply": reply
    }
    
    save_session(request.session_id, session)
    
    response = ClarifyResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        reply=reply
    )
    
    return response

