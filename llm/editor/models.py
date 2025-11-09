from typing import Optional
from pydantic import BaseModel


class EditRequest(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str


class EditResponse(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str
    code: str
    compiler_status: Optional[str] = None

