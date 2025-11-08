from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llm.planner.models import DecideRequest, DecideResponse, QueueStatus
from llm.planner.planner import process_user_request
from llm.planner.queue_manager import get_queue_manager
from llm.clarifier.models import ClarifyRequest, ClarifyResponse
from llm.clarifier.clarifier import process_clarification_request
from llm.actor.models import ActionRequest, ActionResponse
from llm.actor.actor import process_action_request

app = FastAPI(title="LLM Agent API", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/decide", response_model=List[DecideResponse])
async def decide(request: DecideRequest) -> List[DecideResponse]:
    """
    Planner agent endpoint that classifies user intent and enriches prompts.
    Supports multi-task requests and sequential processing per session.

    Input:
    - sid: Session ID
    - text: User query (can contain multiple tasks)

    Output:
    List of DecideResponse objects, one per task:
    - step_id: Unique step identifier
    - step_type: Intent classification (edit/act/clarify)
    - intent: Enriched user query with explanation
    - context: Summarized context from previous prompts
    """
    try:
        responses = await process_user_request(request)
        return responses
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.get("/queue/{sid}", response_model=QueueStatus)
async def get_queue_status(sid: str) -> QueueStatus:
    """
    Get the current status of a session's task queue.

    Input:
    - sid: Session ID (path parameter)

    Output:
    - sid: Session ID
    - pending: List of pending tasks
    - processing: List of currently processing tasks
    - completed: List of completed tasks
    """
    try:
        queue_manager = get_queue_manager()
        status = await queue_manager.get_queue_status(sid)
        return QueueStatus(sid=sid, **status)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting queue status: {str(e)}"
        )


@app.get("/queue/{sid}", response_model=QueueStatus)
async def get_queue_status(sid: str) -> QueueStatus:
    """
    Get the current status of a session's task queue.

    Input:
    - sid: Session ID (path parameter)

    Output:
    - sid: Session ID
    - pending: List of pending tasks
    - processing: List of currently processing tasks
    - completed: List of completed tasks
    """
    try:
        queue_manager = get_queue_manager()
        status = await queue_manager.get_queue_status(sid)
        return QueueStatus(sid=sid, **status)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting queue status: {str(e)}"
        )


@app.post("/clarify", response_model=ClarifyResponse)
async def clarify(request: ClarifyRequest) -> ClarifyResponse:
    """
    Clarification agent endpoint that generates Jarvis-style clarification replies.

    Input:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: User's ambiguous request with explanation
    - context: Previous actions/prompts

    Output:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: Original intent
    - context: Original context
    - reply: Jarvis-style clarification question
    """
    try:
        response = process_clarification_request(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing clarification request: {str(e)}"
        )


@app.post("/action", response_model=ActionResponse)
async def action(request: ActionRequest) -> ActionResponse:
    """
    Actor agent endpoint that generates actions based on intent and context.

    Input:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: User's request with explanation
    - context: Previous actions/prompts

    Output:
    - session_id: Session ID
    - step_id: Step identifier
    - intent: User's request with explanation
    - context: Previous actions/prompts
    - action: Generated action
    """
    try:
        response = process_action_request(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing action request: {str(e)}"
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
