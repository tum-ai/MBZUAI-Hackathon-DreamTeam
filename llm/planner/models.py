from enum import Enum
from pydantic import BaseModel


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

