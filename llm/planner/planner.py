from .models import DecideRequest, DecideResponse, StepType
from .llm_client import classify_intent
from .session_manager import (
    get_previous_context,
    add_prompt_to_session,
    generate_step_id
)


def process_user_request(request: DecideRequest) -> DecideResponse:
    """
    Process user request through the planner agent.
    
    Steps:
    1. Get previous context from session
    2. Call LLM to classify intent and enrich with explanation
    3. Generate step ID
    4. Save current prompt to session
    5. Return structured response
    """
    previous_context = get_previous_context(request.sid)
    
    llm_result = classify_intent(request.text, previous_context)
    
    step_id = generate_step_id(request.sid)
    
    intent = f"{request.text} | {llm_result['explanation']}"
    
    context = llm_result.get('context_summary', '') or previous_context
    
    add_prompt_to_session(request.sid, request.text)
    
    response = DecideResponse(
        step_id=step_id,
        step_type=StepType(llm_result['step_type']),
        intent=intent,
        context=context
    )
    
    return response

