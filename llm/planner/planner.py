from typing import List
from .models import DecideRequest, DecideResponse, StepType
from .llm_client import split_tasks
from .session_manager import (
    get_previous_context,
    add_prompt_to_session,
    generate_step_id,
)
from .queue_manager import get_queue_manager


async def process_single_task(
    task: dict, sid: str, previous_context: str
) -> DecideResponse:
    """
    Process a single task and return DecideResponse.

    Args:
        task: Dict with 'text', 'step_type', 'explanation'
        sid: Session ID
        previous_context: Context from previous prompts
    """
    step_id = task.get("step_id")
    if not step_id:
        step_id = generate_step_id(sid)
        task["step_id"] = step_id

    intent = f"{task['text']} | {task['explanation']}"

    # Use previous context or build from recent prompts
    context = previous_context

    # Add this task text to session history
    add_prompt_to_session(sid, task["text"])

    # Update previous context for next task
    updated_context = get_previous_context(sid)

    response = DecideResponse(
        step_id=step_id,
        step_type=StepType(task["step_type"]),
        intent=intent,
        context=context,
    )

    return response


async def process_user_request(request: DecideRequest) -> List[DecideResponse]:
    """
    Process user request through the planner agent with queue support.

    Steps:
    1. Get previous context from session
    2. Split request into multiple tasks using LLM
    3. Enqueue all tasks
    4. Process tasks sequentially
    5. Return list of structured responses
    """
    previous_context = get_previous_context(request.sid)

    #  split tasks called for all the requests, also if there is one step
    # Split the request into tasks (returns dict with tasks and context_summary)
    # handles both cases: one step and multiple steps
    split_result = split_tasks(request.text, previous_context)
    tasks = split_result["tasks"]

    initial_step_id = request.step_id
    for index, task in enumerate(tasks):
        if index == 0 and initial_step_id:
            task["step_id"] = initial_step_id
        elif not task.get("step_id"):
            task["step_id"] = generate_step_id(request.sid)
    context_summary = split_result.get("context_summary", "")

    # Use context_summary if available, otherwise use previous_context
    # effective_context = context_summary if context_summary else previous_context

    # Get queue manager
    queue_manager = get_queue_manager()

    # Enqueue all tasks
    await queue_manager.enqueue_tasks(request.sid, tasks)

    # sequentially process
    async def processor(task):
        # Get updated context for this task
        current_context = get_previous_context(request.sid)

        if task == tasks[0] and context_summary:
            return await process_single_task(task, request.sid, context_summary)
        return await process_single_task(task, request.sid, current_context)

    responses = await queue_manager.process_all_tasks(request.sid, processor)

    return responses
