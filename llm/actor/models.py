from pydantic import BaseModel


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
