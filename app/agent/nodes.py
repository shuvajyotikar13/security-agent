from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import ToolMessage
from app.agent.state import ThreatAgentState
from app.tools.mcp_client import mcp_session

llm = ChatVertexAI(model="gemini-2.5-pro")

def retrieve_context(state: ThreatAgentState):
    """Mock retrieval for local testing."""
    return {"historical_context": "User flagged an anomaly on IP 10.0.0.5 previously."}

def call_model(state: ThreatAgentState):
    """Executes the LLM with the correct MCP tool definitions."""
    mcp_tool_schemas = [
        {
            "name": "read_query",
            "description": "Run a read-only SQL query against the local database to check logs.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        }
    ]
    
    llm_with_tools = llm.bind_tools(mcp_tool_schemas)
    
    # --- THE FIX: Inject the Schema and Dialect ---
    system_prompt = f"""Context: {state.get('historical_context', '')}
You are an elite SOC Data Agent. 

You have access to a local SQLite database to investigate alerts. 
CRITICAL RULES FOR SQL QUERIES:
1. DIALECT: You MUST use strictly SQLite-compatible syntax (do not use Postgres intervals like '1 day').
2. SCHEMA: There is exactly ONE table available named `network_logs`.
3. COLUMNS: The `network_logs` table has exactly two columns: `ip` (TEXT) and `action` (TEXT). Do NOT invent column names like src_ip.
"""
    
    messages = [{"role": "system", "content": system_prompt}] + list(state["messages"])
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}
async def execute_mcp_tools(state: ThreatAgentState):
    """Intercepts tool calls and routes them dynamically to the local MCP server."""
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return {"messages": []}

    tool_responses = []
    async with mcp_session() as session:
        for tool_call in last_message.tool_calls:
            # We now pass the tool_call["name"] dynamically (which will be 'read_query')
            mcp_result = await session.call_tool(
                tool_call["name"], 
                arguments=tool_call["args"]
            )
            
            tool_responses.append(
                ToolMessage(
                    content=str(mcp_result.content[0].text),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
            
    return {"messages": tool_responses}
