from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


class StepType(str, Enum):
    CLARIFY = "clarify"
    ACT = "act"
    EDIT = "edit"


class DecideRequest(BaseModel):
    sid: str
    text: str


class DecideResponse(BaseModel):
    step_id: str
    step_type: StepType
    intent: str
    context: str


class TaskItem(BaseModel):
    """Individual task in the queue."""
    text: str
    step_type: str
    explanation: str
    status: str
    queued_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

# {
#   "text": "click submit button",
#   "step_type": "act",
#   "explanation": "User wants to click the submit button",
#   "status": "completed",
#   "queued_at": "2024-01-15T10:00:00",
#   "started_at": "2024-01-15T10:00:01",
#   "completed_at": "2024-01-15T10:00:02"
# }


class QueueStatus(BaseModel):
    """Status of a session's task queue."""
    sid: str
    pending: List[TaskItem]
    processing: List[TaskItem]
    completed: List[TaskItem]


# {
#   "sid": "session-123",
#   "pending": [],
#   "processing": [],
#   "completed": [
#     {"text": "scroll down", "status": "completed", ...},
#     {"text": "click submit", "status": "completed", ...}
#   ]
# }


class PlanRequest(BaseModel):
    """Request for executing a full plan through the orchestrator."""
    sid: str
    text: str


class AgentResult(BaseModel):
    """Result from any agent (edit/act/clarify) in unified format."""
    session_id: str
    step_id: str
    intent: str
    context: str
    result: str  # Can be code, action, or reply depending on agent_type
    agent_type: str  # "edit", "act", or "clarify"


class PlanResponse(BaseModel):
    """Response from the plan orchestrator with all agent results."""
    sid: str
    results: List[AgentResult]
