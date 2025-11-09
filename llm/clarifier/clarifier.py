import asyncio
import logging
import sys
from pathlib import Path

from .models import ClarifyRequest, ClarifyResponse
from .llm_client import generate_clarification

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planner.session_manager import load_session, save_session

logger = logging.getLogger(__name__)


async def process_clarification_request(request: ClarifyRequest) -> ClarifyResponse:
    """
    Process clarification request through the Jarvis-style clarifier agent.

    Steps:
    1. Generate clarification reply using LLM with Jarvis personality
    2. Save clarification to session with step_id
    3. Return complete response with reply
    """
    reply = await asyncio.to_thread(
        generate_clarification, request.intent, request.context
    )

    session = load_session(request.session_id)

    if "clarifications" not in session:
        session["clarifications"] = {}

    session["clarifications"][request.step_id] = {
        "intent": request.intent,
        "context": request.context,
        "reply": reply,
    }

    save_session(request.session_id, session)

    response = ClarifyResponse(
        session_id=request.session_id,
        step_id=request.step_id,
        intent=request.intent,
        context=request.context,
        reply=reply,
    )

    try:
        from llm import server as server_module

        await server_module.send_tts_message(reply, request.session_id, request.step_id)
    except Exception as exc:
        logger.warning(
            "Unable to trigger TTS for session %s step %s: %s",
            request.session_id,
            request.step_id,
            exc,
        )

    return response
