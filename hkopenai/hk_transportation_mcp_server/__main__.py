"""
Main entry point for the HK OpenAI Transportation MCP Server.

This module serves as the starting point for running the server, invoking the main function
from the server module to initialize and start the MCP server.
"""

import argparse
import os
from hkopenai.hk_transportation_mcp_server.server import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HK Transportation MCP Server")
    parser.add_argument(
        "-s", "--sse", action="store_true", help="Run in SSE mode instead of stdio"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to bind the server to"
    )
    args = parser.parse_args()

    # Check environment variables for transport mode, host, and port
    if os.environ.get('TRANSPORT_MODE') == 'sse':
        args.sse = True
    if os.environ.get('HOST'):
        args.host = os.environ.get('HOST')
    if os.environ.get('PORT'):
        args.port = int(os.environ.get('PORT'))

    main(args)