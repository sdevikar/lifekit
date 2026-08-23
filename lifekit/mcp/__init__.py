"""lifekit.mcp — MCP server with JSON-RPC stdio transport."""

from lifekit.mcp.server import get_connection, handle_message

__all__ = ["handle_message", "get_connection"]
