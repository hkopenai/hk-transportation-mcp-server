"""
MCP Server module for transportation data in Hong Kong.

This module provides the main server setup for the HK OpenAI Transportation MCP Server,
including tools for fetching passenger statistics, bus routes, and land boundary wait times.
"""

from fastmcp import FastMCP

from hkopenai.hk_transportation_mcp_server import (
    tool_passenger_traffic,
    tool_bus_kmb,
    tool_land_custom_wait_time,
)


def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI transportation Server")

    tool_passenger_traffic.register(mcp)
    tool_bus_kmb.register(mcp)
    tool_land_custom_wait_time.register(mcp)

    return mcp


def main(host: str, port: int, sse: bool):
    """
    Main function to start the MCP Server.

    Args:
        args: Command line arguments passed to the function.
    """
    server = create_mcp_server()

    if sse:
        server.run(transport="streamable-http", host=host, port=port)
        print(
            f"HK Transportation MCP Server running in SSE mode on port {port}, bound to {host}"
        )
    else:
        server.run()
        print("HK Transportation MCP Server running in stdio mode")
