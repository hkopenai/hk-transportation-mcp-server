"""Unit tests for Land Boundary Control Points Waiting Time tool."""

import unittest
from unittest.mock import patch, MagicMock
from hkopenai.hk_transportation_mcp_server import tool_land_custom_wait_time

class TestLandCustomWaitTimeTool(unittest.TestCase):
    def setUp(self):
        self.tool = tool_land_custom_wait_time.LandCustomWaitTimeTool()

    def test_init(self):
        self.assertEqual(self.tool.name, "get_land_boundary_wait_times")
        self.assertEqual(self.tool.description, "Fetch current waiting times at land boundary control points in Hong Kong.")

    @patch('requests.get')
    def test_execute(self, mock_get):
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "HYW": {"arrQueue": 0, "depQueue": 0},
            "HZM": {"arrQueue": 1, "depQueue": 1},
            "LMC": {"arrQueue": 2, "depQueue": 2},
            "LSC": {"arrQueue": 0, "depQueue": 0},
            "LWS": {"arrQueue": 0, "depQueue": 0},
            "MKT": {"arrQueue": 0, "depQueue": 0},
            "SBC": {"arrQueue": 0, "depQueue": 0},
            "STK": {"arrQueue": 99, "depQueue": 99}
        }
        mock_get.return_value = mock_response

        # Execute the tool
        result = self.tool.execute({"lang": "en"})

        # Check if the result contains expected formatted output
        self.assertIn("Land Boundary Control Points Waiting Times (EN)", result)
        self.assertIn("Heung Yuen Wai (HYW)", result)
        self.assertIn("Arrival: Normal (Generally less than 15 mins)", result)
        self.assertIn("Sha Tau Kok (STK)", result)
        self.assertIn("Arrival: Non Service Hours", result)

if __name__ == '__main__':
    unittest.main()
