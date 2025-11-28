from typing import TypedDict, List, Annotated
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_action: dict  # {type: "tool", name: "...", args: {...}} OR {type: "finish", content: "..."}
    session_id: str
    results: Annotated[List[dict], operator.add]  # Track results directly
