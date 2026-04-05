from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@asynccontextmanager
async def mcp_session():
    """
    Spins up an ephemeral local MCP server for the laptop demo.
    Uses the official Python SQLite MCP server.
    """
    server_params = StdioServerParameters(
        command="mcp-server-sqlite",
        args=["--db-path", "local_logs.db"], # Updated to match the Python server arguments
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session
