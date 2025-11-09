import logging
import sys
import time
from typing import List
from llm.planner.models import (
    PlanRequest,
    PlanResponse,
    AgentResult,
    DecideRequest,
    StepType,
    TimingMetadata,
)
from llm.planner.planner import process_user_request
from llm.editor.models import EditRequest
from llm.editor.editor import process_edit_request
from llm.actor.models import ActionRequest
from llm.actor.actor import process_action_request
from llm.clarifier.models import ClarifyRequest
from llm.clarifier.clarifier import process_clarification_request

# Configure logger to ensure it outputs to stdout
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


async def execute_plan(request: PlanRequest) -> PlanResponse:
    """
    Execute the full plan orchestration pipeline.

    Steps:
    1. Log request received
    2. Call planner to get list of tasks (with timing)
    3. For each task, route to appropriate agent based on step_type (with timing)
    4. Collect all results with timing metadata
    5. Return aggregated response with detailed timing

    Args:
        request: PlanRequest with session_id and text

    Returns:
        PlanResponse with all agent results and timing metadata

    Raises:
        Exception: Any error from planner or agents (fail fast)
    """
    overall_start = time.time()
    logger.info(f"Plan request received for session: {request.sid}")

    # Time the planner
    decide_request = DecideRequest(
        sid=request.sid,
        text=request.text,
        step_id=request.step_id,
    )
    logger.info(f"Calling planner for session: {request.sid}")

    planner_start = time.time()
    decide_responses = await process_user_request(decide_request)
    planner_duration = time.time() - planner_start

    logger.info(
        f"Planner identified {len(decide_responses)} task(s) for session: {request.sid} in {planner_duration:.3f}s"
    )

    results: List[AgentResult] = []
    task_timings = []

    for idx, decide_response in enumerate(decide_responses):
        step_id = decide_response.step_id
        step_type = decide_response.step_type
        intent = decide_response.intent
        context = decide_response.context

        logger.info(
            f"Processing task {idx + 1}/{len(decide_responses)} - Step ID: {step_id}, Type: {step_type}"
        )

        agent_start = time.time()

        if step_type == StepType.EDIT:
            logger.info(f"Routing to EDIT agent for step: {step_id}")
            edit_request = EditRequest(
                session_id=request.sid, step_id=step_id, intent=intent, context=context
            )
            edit_response = await process_edit_request(edit_request)

            agent_duration = time.time() - agent_start

            agent_result = AgentResult(
                session_id=edit_response.session_id,
                step_id=edit_response.step_id,
                intent=edit_response.intent,
                context=edit_response.context,
                result=edit_response.code,
                agent_type="edit",
                execution_time_seconds=round(agent_duration, 3),
            )
            results.append(agent_result)
            task_timings.append(
                {
                    "step_id": step_id,
                    "agent_type": "edit",
                    "duration_seconds": round(agent_duration, 3),
                }
            )
            logger.info(
                f"EDIT agent completed for step: {step_id} in {agent_duration:.3f}s"
            )

        elif step_type == StepType.ACT:
            logger.info(f"Routing to ACT agent for step: {step_id}")
            action_request = ActionRequest(
                session_id=request.sid, step_id=step_id, intent=intent, context=context
            )
            action_response = await process_action_request(action_request)

            agent_duration = time.time() - agent_start

            agent_result = AgentResult(
                session_id=action_response.session_id,
                step_id=action_response.step_id,
                intent=action_response.intent,
                context=action_response.context,
                result=action_response.action,
                agent_type="act",
                execution_time_seconds=round(agent_duration, 3),
            )
            results.append(agent_result)
            task_timings.append(
                {
                    "step_id": step_id,
                    "agent_type": "act",
                    "duration_seconds": round(agent_duration, 3),
                }
            )
            logger.info(
                f"ACT agent completed for step: {step_id} in {agent_duration:.3f}s"
            )

        elif step_type == StepType.CLARIFY:
            logger.info(f"Routing to CLARIFY agent for step: {step_id}")
            clarify_request = ClarifyRequest(
                session_id=request.sid, step_id=step_id, intent=intent, context=context
            )
            clarify_response = await process_clarification_request(clarify_request)

            agent_duration = time.time() - agent_start

            agent_result = AgentResult(
                session_id=clarify_response.session_id,
                step_id=clarify_response.step_id,
                intent=clarify_response.intent,
                context=clarify_response.context,
                result=clarify_response.reply,
                agent_type="clarify",
                execution_time_seconds=round(agent_duration, 3),
            )
            results.append(agent_result)
            task_timings.append(
                {
                    "step_id": step_id,
                    "agent_type": "clarify",
                    "duration_seconds": round(agent_duration, 3),
                }
            )
            logger.info(
                f"CLARIFY agent completed for step: {step_id} in {agent_duration:.3f}s"
            )

        else:
            logger.warning(f"Unknown step_type: {step_type} for step: {step_id}")

    # Calculate timing metadata
    overall_duration = time.time() - overall_start
    total_agent_time = sum(t["duration_seconds"] for t in task_timings)

    timing_metadata = TimingMetadata(
        planner_time_seconds=round(planner_duration, 3),
        total_agent_time_seconds=round(total_agent_time, 3),
        total_time_seconds=round(overall_duration, 3),
        task_timings=task_timings,
    )

    response = PlanResponse(sid=request.sid, results=results, timing=timing_metadata)
    logger.info(
        f"Plan execution completed for session: {request.sid} with {len(results)} result(s) in {overall_duration:.3f}s (planner: {planner_duration:.3f}s, agents: {total_agent_time:.3f}s)"
    )

    return response
