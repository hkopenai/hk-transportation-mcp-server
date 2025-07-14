"""
Main entry point for the HK OpenAI Transportation MCP Server.

This module serves as the starting point for running the server, invoking the main function
from the server module to initialize and start the MCP server.
"""

from hkopenai_common.cli_utils import cli_main
from .server import server

if __name__ == "__main__":
    cli_main(server, "HK Transportation MCP Server")
