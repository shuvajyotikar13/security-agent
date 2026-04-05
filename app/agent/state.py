from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ThreatAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    historical_context: str
