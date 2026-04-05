"""
Agent Tools Package.
Contains the interfaces and connection managers for the Model Context Protocol (MCP).
"""

# Expose the mcp_session context manager at the package level for cleaner imports
from .mcp_client import mcp_session

__all__ = ["mcp_session"]
