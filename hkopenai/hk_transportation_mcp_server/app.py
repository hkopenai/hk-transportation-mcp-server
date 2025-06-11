import argparse
from fastmcp import FastMCP
from hkopenai.hk_transportation_mcp_server import tool_business_reg, tool_passenger_traffic
from typing import Dict, Annotated, Optional
from pydantic import Field

def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI transportation Server")

    @mcp.tool(
        description="Get monthly statistics on the number of new business registrations in Hong Kong"
    )
    def get_business_stats(
        start_year: Annotated[Optional[int], Field(description="Start Year")] = None,
        start_month: Annotated[Optional[int], Field(description="Start Month")] = None,
        end_year: Annotated[Optional[int], Field(description="End Year")] = None,
        end_month: Annotated[Optional[int], Field(description="End Month")] = None
    ) -> Dict:
        return tool_business_reg.get_business_stats(start_year, start_month, end_year, end_month)

    @mcp.tool(
        description="The statistics on daily passenger traffic provides figures concerning daily statistics on inbound and outbound passenger trips at all control points since 2021 (with breakdown by Hong Kong Residents, Mainland Visitors and Other Visitors). Return last 7 days data if no date range is specified."
    )
    def get_passenger_stats(
        start_date: Annotated[Optional[str], Field(description="Start date in DD-MM-YYYY format")] = None,
        end_date: Annotated[Optional[str], Field(description="End date in DD-MM-YYYY format")] = None
    ) -> Dict:
        return tool_passenger_traffic.get_passenger_stats(start_date, end_date)

    return mcp

def main():
    parser = argparse.ArgumentParser(description='HKO MCP Server')
    parser.add_argument('-s', '--sse', action='store_true',
                       help='Run in SSE mode instead of stdio')
    args = parser.parse_args()

    server = create_mcp_server()
    
    if args.sse:
        server.run(transport="streamable-http")
        print("HKO MCP Server running in SSE mode on port 8000")
    else:
        server.run()
        print("HKO MCP Server running in stdio mode")

if __name__ == "__main__":
    main()
