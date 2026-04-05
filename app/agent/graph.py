from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from app.agent.state import ThreatAgentState
from app.agent.nodes import retrieve_context, call_model, execute_mcp_tools

workflow = StateGraph(ThreatAgentState)

workflow.add_node("retrieve", retrieve_context)
workflow.add_node("agent", call_model)
workflow.add_node("tools", execute_mcp_tools)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")
