from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import ToolMessage
from app.agent.state import ThreatAgentState
from app.tools.mcp_client import mcp_session

llm = ChatVertexAI(model="gemini-2.5-pro")

def retrieve_context(state: ThreatAgentState):
    """Mock retrieval for local testing."""
    return {"historical_context": "User flagged an anomaly on IP 10.0.0.5 previously."}

def call_model(state: ThreatAgentState):
    """Executes the LLM with mocked tool definitions."""
    mcp_tool_schemas = [
        {
            "name": "query-database",
            "description": "Run a read-only SQL query against the local database to check logs.",
            "parameters": {
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"],
            },
        }
    ]
    
    llm_with_tools = llm.bind_tools(mcp_tool_schemas)
    system_prompt = f"Context: {state.get('historical_context', '')}\n You are a SOC Data Agent."
    
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}

async def execute_mcp_tools(state: ThreatAgentState):
    """Intercepts tool calls and routes them to the local MCP server."""
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return {"messages": []}

    tool_responses = []
    async with mcp_session() as session:
        for tool_call in last_message.tool_calls:
            # Map LLM tool call to MCP tool call
            mcp_result = await session.call_tool("query-database", arguments=tool_call["args"])
            
            tool_responses.append(
                ToolMessage(
                    content=str(mcp_result.content[0].text),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
            
    return {"messages": tool_responses}
