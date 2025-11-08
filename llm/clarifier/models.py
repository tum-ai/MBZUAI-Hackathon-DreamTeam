from pydantic import BaseModel


class ClarifyRequest(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str


class ClarifyResponse(BaseModel):
    session_id: str
    step_id: str
    intent: str
    context: str
    reply: str

