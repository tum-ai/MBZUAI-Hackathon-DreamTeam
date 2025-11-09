from pydantic import BaseModel
from typing import Optional


class ActionRequest(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str


class ActionResponse(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str
    action: str
    automation_status: Optional[str] = None
