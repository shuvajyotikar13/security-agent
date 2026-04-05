import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from app.agent.state import ThreatAgentState
from app.agent.nodes import retrieve_context, call_model, execute_mcp_tools

# Connect local SQLite for short-term thread memory
conn = sqlite3.connect("short_term_memory.db", check_same_thread=False)
memory_saver = SqliteSaver(conn)

workflow = StateGraph(ThreatAgentState)

workflow.add_node("retrieve", retrieve_context)
workflow.add_node("agent", call_model)
workflow.add_node("tools", execute_mcp_tools)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# Compile the graph
agent_app = workflow.compile(checkpointer=memory_saver)
