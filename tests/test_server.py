import unittest
from unittest.mock import patch, Mock
from hkopenai.hk_transportation_mcp_server.server import create_mcp_server

class TestApp(unittest.TestCase):
    @patch('hkopenai.hk_transportation_mcp_server.server.FastMCP')
    @patch('hkopenai.hk_transportation_mcp_server.server.tool_passenger_traffic')
    @patch('hkopenai.hk_transportation_mcp_server.server.tool_bus_kmb')
    @patch('hkopenai.hk_transportation_mcp_server.server.tool_land_custom_wait_time')
    def test_create_mcp_server(self, mock_tool_land_custom_wait_time, mock_tool_bus_kmb, mock_tool_passenger_traffic, mock_fastmcp):
        # Setup mocks
        mock_server = Mock()
        
        # Configure mock_server.tool to return a mock that acts as the decorator
        # This mock will then be called with the function to be decorated
        mock_server.tool.return_value = Mock()
        mock_fastmcp.return_value = mock_server

        # Test server creation
        server = create_mcp_server()

        # Verify server creation
        mock_fastmcp.assert_called_once()
        self.assertEqual(server, mock_server)

        # Verify that the tool decorator was called for each tool function
        self.assertEqual(mock_server.tool.call_count, 3)

        # Get all decorated functions
        decorated_funcs = {call.args[0].__name__: call.args[0] for call in mock_server.tool.return_value.call_args_list}
        self.assertEqual(len(decorated_funcs), 3)

        # Call each decorated function and verify that the correct underlying function is called
        
        decorated_funcs['get_passenger_stats'](start_date="01-01-2023", end_date="31-01-2023")
        mock_tool_passenger_traffic.get_passenger_stats.assert_called_once_with("01-01-2023", "31-01-2023")

        decorated_funcs['get_bus_kmb'](lang="en")
        mock_tool_bus_kmb.get_bus_kmb.assert_called_once_with("en")

        decorated_funcs['get_land_boundary_wait_times'](lang="tc")
        mock_tool_land_custom_wait_time.register_tools.return_value[0].execute.assert_called_once_with({"lang": "tc"})

if __name__ == "__main__":
    unittest.main()
