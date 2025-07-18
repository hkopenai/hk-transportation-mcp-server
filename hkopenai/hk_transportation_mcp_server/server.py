"""
MCP Server module for transportation data in Hong Kong.

This module provides the main server setup for the HK OpenAI Transportation MCP Server,
including tools for fetching passenger statistics, bus routes, and land boundary wait times.
"""

from fastmcp import FastMCP

from .tools import (
    passenger_traffic,
    bus_kmb,
    land_custom_wait_time,
)


def server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI transportation Server")

    passenger_traffic.register(mcp)
    bus_kmb.register(mcp)
    land_custom_wait_time.register(mcp)

    return mcp
