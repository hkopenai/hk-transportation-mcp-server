"""
Unit tests for the HK OpenAI Transportation MCP Server.

This module tests the server creation and tool registration functionality
to ensure that the MCP server is properly initialized with the expected tools.
"""

import unittest
from unittest.mock import patch, Mock
from hkopenai.hk_transportation_mcp_server.server import server


class TestApp(unittest.TestCase):
    """
    Test class for verifying the functionality of the MCP server setup.

    This class contains tests to ensure that the server is created correctly
    and that the tools are properly registered and functional.
    """

    @patch("hkopenai.hk_transportation_mcp_server.server.FastMCP")
    @patch("hkopenai.hk_transportation_mcp_server.tools.passenger_traffic")
    @patch("hkopenai.hk_transportation_mcp_server.tools.bus_kmb")
    @patch("hkopenai.hk_transportation_mcp_server.tools.land_custom_wait_time")
    def test_create_mcp_server(
        self,
        mock_tool_land_custom_wait_time,
        mock_tool_bus_kmb,
        mock_tool_passenger_traffic,
        mock_fastmcp,
    ):
        """
        Test the creation of the MCP server and registration of tools.

        This test verifies that the server is initialized correctly, and that
        the tools for passenger statistics, bus routes, and boundary wait times
        are properly registered and callable with the expected parameters.

        Args:
            mock_tool_land_custom_wait_time: Mock for the land custom wait time tool.
            mock_tool_bus_kmb: Mock for the bus KMB tool.
            mock_tool_passenger_traffic: Mock for the passenger traffic tool.
            mock_fastmcp: Mock for the FastMCP server class.
        """
        # Setup mocks
        mock_mcp = Mock()

        mock_fastmcp.return_value = mock_mcp

        # Test server creation
        server("localhost", 8000, False)

        # Verify server creation
        mock_fastmcp.assert_called_once()

        mock_tool_passenger_traffic.register.assert_called_once_with(mock_mcp)
        mock_tool_bus_kmb.register.assert_called_once_with(mock_mcp)
        mock_tool_land_custom_wait_time.register.assert_called_once_with(mock_mcp)


if __name__ == "__main__":
    unittest.main()
