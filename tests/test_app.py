import unittest
from unittest.mock import patch, Mock
from hkopenai.hk_transportation_mcp_server.app import create_mcp_server
from hkopenai.hk_transportation_mcp_server.tool_passenger_traffic import fetch_passenger_traffic_data

def create_tool_decorator(expected_name, decorated_funcs):
    """Create a tool decorator that only matches functions with the expected name.
    
    Args:
        expected_name: The function name to match
        decorated_funcs: List to append matched functions to
    """
    def tool_decorator(description=None):
        def decorator(f):
            if f.__name__ == expected_name:
                decorated_funcs.append(f)
            return f
        return decorator
    return tool_decorator

class TestApp(unittest.TestCase):
    @patch('hkopenai.hk_transportation_mcp_server.app.FastMCP')
    @patch('hkopenai.hk_transportation_mcp_server.app.tool_passenger_traffic')
    def test_create_mcp_server(self, mock_tool_passenger, mock_fastmcp):
        # Setup mocks
        mock_server = unittest.mock.Mock()
        
        # Track decorator calls and capture decorated functions
        decorator_calls = []
        decorated_funcs = []
        
        tool_decorator = create_tool_decorator('get_passenger_stats', decorated_funcs)
            
        mock_server.tool = tool_decorator
        mock_fastmcp.return_value = mock_server
        mock_tool_passenger.get_passenger_stats.return_value = {'passenger': 'data'}

        # Test server creation
        server = create_mcp_server()

        # Verify server creation
        mock_fastmcp.assert_called_once_with(name="HK OpenAI transportation Server")
        self.assertEqual(server, mock_server)
        
        # Test the passenger traffic tool
        passenger_result = decorated_funcs[0]()
        mock_tool_passenger.get_passenger_stats.assert_called_once()

    @patch('hkopenai.hk_transportation_mcp_server.app.FastMCP')
    @patch('hkopenai.hk_transportation_mcp_server.app.tool_passenger_traffic')
    def test_get_passenger_stats(self, mock_tool_passenger, mock_fastmcp):
        # Setup mocks
        mock_server = unittest.mock.Mock()
        decorated_funcs = []
        
        tool_decorator = create_tool_decorator('get_passenger_stats', decorated_funcs)
            
        mock_server.tool = tool_decorator
        mock_fastmcp.return_value = mock_server
        
        # Test default behavior
        mock_tool_passenger.get_passenger_stats.return_value = {'data': 'last_7_days'}
        server = create_mcp_server()
        passenger_func = decorated_funcs[0]  # get_passenger_stats is the second tool
        result = passenger_func()
        mock_tool_passenger.get_passenger_stats.assert_called_once_with(None, None)
        self.assertEqual(result, {'data': 'last_7_days'})

        # Test with date range
        mock_tool_passenger.get_passenger_stats.reset_mock()
        mock_tool_passenger.get_passenger_stats.return_value = {'data': 'date_range'}
        result = passenger_func(start_date='01-01-2025', end_date='31-01-2025')
        mock_tool_passenger.get_passenger_stats.assert_called_once_with('01-01-2025', '31-01-2025')
        self.assertEqual(result, {'data': 'date_range'})

        # Test invalid date format
        mock_tool_passenger.get_passenger_stats.reset_mock()
        mock_tool_passenger.get_passenger_stats.side_effect = ValueError('Invalid date format')
        with self.assertRaises(ValueError):
            passenger_func(start_date='2025-01-01')  # Wrong format

    @patch('hkopenai.hk_transportation_mcp_server.app.FastMCP')
    @patch('hkopenai.hk_transportation_mcp_server.app.tool_bus_kmb')
    def test_get_bus_kmb(self, mock_tool_bus, mock_fastmcp):
        # Setup mocks
        mock_server = unittest.mock.Mock()
        decorated_funcs = []
        
        tool_decorator = create_tool_decorator('get_bus_kmb', decorated_funcs)
            
        mock_server.tool = tool_decorator
        mock_fastmcp.return_value = mock_server
        
        # Test default behavior
        mock_tool_bus.get_bus_kmb.return_value = {'data': 'bus_routes'}
        server = create_mcp_server()
        bus_func = decorated_funcs[0]  # get_bus_kmb is the second tool
        result = bus_func()
        mock_tool_bus.get_bus_kmb.assert_called_once_with('en')
        self.assertEqual(result, {'data': 'bus_routes'})

        # Test with language parameter
        mock_tool_bus.get_bus_kmb.reset_mock()
        mock_tool_bus.get_bus_kmb.return_value = {'data': 'bus_routes_tc'}
        result = bus_func(lang='tc')
        mock_tool_bus.get_bus_kmb.assert_called_once_with('tc')
        self.assertEqual(result, {'data': 'bus_routes_tc'})

    @patch('hkopenai.hk_transportation_mcp_server.app.FastMCP')
    @patch('hkopenai.hk_transportation_mcp_server.app.tool_land_custom_wait_time')
    def test_get_land_boundary_wait_times(self, mock_tool_land, mock_fastmcp):
        # Setup mocks
        mock_server = unittest.mock.Mock()
        decorated_funcs = []
        
        tool_decorator = create_tool_decorator('get_land_boundary_wait_times', decorated_funcs)
            
        mock_server.tool = tool_decorator
        mock_fastmcp.return_value = mock_server
        
        # Test default behavior
        mock_tool_land.register_tools.return_value = [Mock()]
        mock_tool_land.register_tools.return_value[0].execute.return_value = "Waiting times data"
        server = create_mcp_server()
        wait_time_func = decorated_funcs[0]  # get_land_boundary_wait_times is the third tool
        result = wait_time_func()
        mock_tool_land.register_tools.return_value[0].execute.assert_called_once_with({"lang": "en"})
        self.assertEqual(result, "Waiting times data")

        # Test with language parameter
        mock_tool_land.register_tools.return_value[0].execute.reset_mock()
        mock_tool_land.register_tools.return_value[0].execute.return_value = "Waiting times data in TC"
        result = wait_time_func(lang='tc')
        mock_tool_land.register_tools.return_value[0].execute.assert_called_once_with({"lang": "tc"})
        self.assertEqual(result, "Waiting times data in TC")

if __name__ == "__main__":
    unittest.main()
