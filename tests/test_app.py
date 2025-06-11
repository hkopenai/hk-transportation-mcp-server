import unittest
from unittest.mock import patch, Mock
from hkopenai.hk_transportation_mcp_server.app import create_mcp_server
from hkopenai.hk_transportation_mcp_server.tool_passenger_traffic import fetch_passenger_traffic_data

class TestApp(unittest.TestCase):
    @patch('hkopenai.hk_transportation_mcp_server.app.FastMCP')
    @patch('hkopenai.hk_transportation_mcp_server.app.tool_business_reg')
    @patch('hkopenai.hk_transportation_mcp_server.app.tool_passenger_traffic')
    def test_create_mcp_server(self, mock_tool_passenger, mock_tool_business, mock_fastmcp):
        # Setup mocks
        mock_server = unittest.mock.Mock()
        
        # Track decorator calls and capture decorated functions
        decorator_calls = []
        decorated_funcs = []
        
        def tool_decorator(description=None):
            # First call: @tool(description=...)
            decorator_calls.append(((), {'description': description}))
            
            def decorator(f):
                # Second call: decorator(function)
                decorated_funcs.append(f)
                return f
                
            return decorator
            
        mock_server.tool = tool_decorator
        mock_fastmcp.return_value = mock_server
        mock_tool_business.get_business_stats.return_value = {'business': 'data'}
        mock_tool_passenger.get_passenger_stats.return_value = {'passenger': 'data'}

        # Test server creation
        server = create_mcp_server()

        # Verify server creation
        mock_fastmcp.assert_called_once_with(name="HK OpenAI transportation Server")
        self.assertEqual(server, mock_server)

        # Verify tools were decorated (2 tools)
        self.assertEqual(len(decorated_funcs), 2)
        
        # Test the business stats tool
        business_result = decorated_funcs[0]()
        mock_tool_business.get_business_stats.assert_called_once()
        
        # Test the passenger traffic tool
        passenger_result = decorated_funcs[1]()
        mock_tool_passenger.get_passenger_stats.assert_called_once()
        
        # Verify tool descriptions were passed to decorator
        self.assertEqual(len(decorator_calls), 2)
        self.assertIsNotNone(decorator_calls[0][1]['description'])
        self.assertIsNotNone(decorator_calls[1][1]['description'])

    @patch('hkopenai.hk_transportation_mcp_server.app.FastMCP')
    @patch('hkopenai.hk_transportation_mcp_server.app.tool_business_reg')
    @patch('hkopenai.hk_transportation_mcp_server.app.tool_passenger_traffic')
    def test_get_passenger_stats(self, mock_tool_passenger, mock_tool_business, mock_fastmcp):
        # Setup mocks
        mock_server = unittest.mock.Mock()
        decorated_funcs = []
        
        def tool_decorator(description=None):
            def decorator(f):
                decorated_funcs.append(f)
                return f
            return decorator
            
        mock_server.tool = tool_decorator
        mock_fastmcp.return_value = mock_server
        
        # Test default behavior
        mock_tool_passenger.get_passenger_stats.return_value = {'data': 'last_7_days'}
        server = create_mcp_server()
        passenger_func = decorated_funcs[1]  # get_passenger_stats is the second tool
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

if __name__ == "__main__":
    unittest.main()
