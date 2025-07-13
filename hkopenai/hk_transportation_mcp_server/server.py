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
from typing import Dict, Annotated, Optional
from pydantic import Field


def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI transportation Server")

    @mcp.tool(
        description="The statistics on daily passenger traffic provides figures concerning daily statistics on inbound and outbound passenger trips at all control points since 2021 (with breakdown by Hong Kong Residents, Mainland Visitors and Other Visitors). Return last 7 days data if no date range is specified."
    )
    def get_passenger_stats(
        start_date: Annotated[
            Optional[str], Field(description="Start date in DD-MM-YYYY format")
        ] = None,
        end_date: Annotated[
            Optional[str], Field(description="End date in DD-MM-YYYY format")
        ] = None,
    ) -> Dict:
        return tool_passenger_traffic.get_passenger_stats(start_date, end_date)

    @mcp.tool(
        description="All bus routes of Kowloon Motor Bus (KMB) and Long Win Bus Services Hong Kong. Data source: Kowloon Motor Bus and Long Win Bus Services"
    )
    def get_bus_kmb(
        lang: Annotated[
            Optional[str],
            Field(
                description="Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
                json_schema_extra={"enum": ["en", "tc", "sc"]},
            ),
        ] = "en",
    ) -> Dict:
        return tool_bus_kmb.get_bus_kmb(lang)

    @mcp.tool(
        description="Fetch current waiting times at land boundary control points in Hong Kong."
    )
    def get_land_boundary_wait_times(
        lang: Annotated[
            Optional[str],
            Field(
                description="Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
                json_schema_extra={"enum": ["en", "tc", "sc"]},
            ),
        ] = "en",
    ) -> Dict:
        return tool_land_custom_wait_time.register_tools()[0].execute({"lang": lang})

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
        print(f"HK Transportation MCP Server running in SSE mode on port {args.port}, bound to {args.host}") 
    else:
        server.run()
        print("HK Transportation MCP Server running in stdio mode")


if __name__ == "__main__":
    main()
