"""Unit tests for Land Boundary Control Points Waiting Time tool."""

import unittest
from unittest.mock import patch, MagicMock
from hkopenai.hk_transportation_mcp_server import tool_land_custom_wait_time


class TestLandCustomWaitTimeTool(unittest.TestCase):
    """
    Test class for verifying the functionality of the Land Boundary Control Points Waiting Time tool.
    
    This class contains tests to ensure that the tool correctly fetches and formats waiting time data
    for different languages and handles various error conditions.
    """
    def setUp(self):
        """
        Set up test fixtures before each test method.
        
        This method initializes the LandCustomWaitTimeTool instance for use in tests.
        """
        self.tool = tool_land_custom_wait_time.LandCustomWaitTimeTool()

    def test_init(self):
        """
        Test the initialization of the LandCustomWaitTimeTool.
        
        This test verifies that the tool is initialized with the correct name and description.
        """
        self.assertEqual(self.tool.name, "get_land_boundary_wait_times")
        self.assertEqual(
            self.tool.description,
            "Fetch current waiting times at land boundary control points in Hong Kong.",
        )

    @patch("requests.get")
    def test_execute(self, mock_get):
        """
        Test the execution of the tool to fetch waiting times in English.
        
        Args:
            mock_get: Mock object for the requests.get function to simulate API responses.
        """
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
            "STK": {"arrQueue": 99, "depQueue": 99},
        }
        mock_get.return_value = mock_response

        # Execute the tool
        result = self.tool.execute({"lang": "en"})

        # Check if the result contains expected JSON structure and data
        self.assertTrue(isinstance(result, dict))
        result_dict = result if isinstance(result, dict) else {}
        type_val = result_dict["type"] if "type" in result_dict else ""
        version_val = result_dict["version"] if "version" in result_dict else ""
        self.assertEqual(type_val, "WaitTimes")
        self.assertEqual(version_val, "1.0")
        data = result_dict["data"] if "data" in result_dict else {}
        self.assertTrue(isinstance(data, dict))
        data_dict = data if isinstance(data, dict) else {}
        language_val = data_dict["language"] if "language" in data_dict else ""
        self.assertEqual(language_val, "EN")
        control_points = data_dict["control_points"] if "control_points" in data_dict else []
        self.assertTrue(isinstance(control_points, list))
        hyw = next((cp for cp in control_points if isinstance(cp, dict) and "code" in cp and cp["code"] == "HYW"), {})
        stk = next((cp for cp in control_points if isinstance(cp, dict) and "code" in cp and cp["code"] == "STK"), {})
        self.assertTrue(isinstance(hyw, dict))
        self.assertTrue(isinstance(stk, dict))
        hyw_dict = hyw if isinstance(hyw, dict) else {}
        stk_dict = stk if isinstance(stk, dict) else {}
        hyw_arrival = hyw_dict["arrival"] if "arrival" in hyw_dict else ""
        stk_arrival = stk_dict["arrival"] if "arrival" in stk_dict else ""
        self.assertEqual(hyw_arrival, "Normal (Generally less than 15 mins)")
        self.assertEqual(stk_arrival, "Non Service Hours")

    @patch("requests.get")
    def test_execute_tc_language(self, mock_get):
        """
        Test the execution of the tool to fetch waiting times in Traditional Chinese.
        
        Args:
            mock_get: Mock object for the requests.get function to simulate API responses.
        """
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "HYW": {"arrQueue": 0, "depQueue": 0},
            "HZM": {"arrQueue": 1, "depQueue": 1},
        }
        mock_get.return_value = mock_response

        # Execute the tool with Traditional Chinese
        result = self.tool.execute({"lang": "tc"})

        # Check if the result contains expected JSON structure and data
        self.assertTrue(isinstance(result, dict))
        result_dict = result if isinstance(result, dict) else {}
        type_val = result_dict["type"] if "type" in result_dict else ""
        version_val = result_dict["version"] if "version" in result_dict else ""
        self.assertEqual(type_val, "WaitTimes")
        self.assertEqual(version_val, "1.0")
        data = result_dict["data"] if "data" in result_dict else {}
        self.assertTrue(isinstance(data, dict))
        data_dict = data if isinstance(data, dict) else {}
        language_val = data_dict["language"] if "language" in data_dict else ""
        self.assertEqual(language_val, "TC")
        control_points = data_dict["control_points"] if "control_points" in data_dict else []
        self.assertTrue(isinstance(control_points, list))
        hyw = next((cp for cp in control_points if isinstance(cp, dict) and "code" in cp and cp["code"] == "HYW"), {})
        self.assertTrue(isinstance(hyw, dict))
        hyw_dict = hyw if isinstance(hyw, dict) else {}
        hyw_arrival = hyw_dict["arrival"] if "arrival" in hyw_dict else ""
        self.assertEqual(hyw_arrival, "Normal (Generally less than 15 mins)")

    @patch("requests.get")
    def test_execute_sc_language(self, mock_get):
        """
        Test the execution of the tool to fetch waiting times in Simplified Chinese.
        
        Args:
            mock_get: Mock object for the requests.get function to simulate API responses.
        """
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "HYW": {"arrQueue": 0, "depQueue": 0},
            "HZM": {"arrQueue": 1, "depQueue": 1},
        }
        mock_get.return_value = mock_response

        # Execute the tool with Simplified Chinese
        result = self.tool.execute({"lang": "sc"})

        # Check if the result contains expected JSON structure and data
        self.assertTrue(isinstance(result, dict))
        result_dict = result if isinstance(result, dict) else {}
        type_val = result_dict["type"] if "type" in result_dict else ""
        version_val = result_dict["version"] if "version" in result_dict else ""
        self.assertEqual(type_val, "WaitTimes")
        self.assertEqual(version_val, "1.0")
        data = result_dict["data"] if "data" in result_dict else {}
        self.assertTrue(isinstance(data, dict))
        data_dict = data if isinstance(data, dict) else {}
        language_val = data_dict["language"] if "language" in data_dict else ""
        self.assertEqual(language_val, "SC")
        control_points = data_dict["control_points"] if "control_points" in data_dict else []
        self.assertTrue(isinstance(control_points, list))
        hyw = next((cp for cp in control_points if isinstance(cp, dict) and "code" in cp and cp["code"] == "HYW"), {})
        self.assertTrue(isinstance(hyw, dict))
        hyw_dict = hyw if isinstance(hyw, dict) else {}
        hyw_arrival = hyw_dict["arrival"] if "arrival" in hyw_dict else ""
        self.assertEqual(hyw_arrival, "Normal (Generally less than 15 mins)")

    @patch("requests.get")
    def test_invalid_language_code(self, mock_get):
        """
        Test the execution of the tool with an invalid language code, expecting default formatting.
        
        Args:
            mock_get: Mock object for the requests.get function to simulate API responses.
        """
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.json.return_value = {"HYW": {"arrQueue": 0, "depQueue": 0}}
        mock_get.return_value = mock_response

        # Execute the tool with invalid language code
        result = self.tool.execute({"lang": "xx"})

        # Should default to English
        self.assertTrue(isinstance(result, dict))
        result_dict = result if isinstance(result, dict) else {}
        type_val = result_dict["type"] if "type" in result_dict else ""
        version_val = result_dict["version"] if "version" in result_dict else ""
        self.assertEqual(type_val, "WaitTimes")
        self.assertEqual(version_val, "1.0")
        data = result_dict["data"] if "data" in result_dict else {}
        self.assertTrue(isinstance(data, dict))
        data_dict = data if isinstance(data, dict) else {}
        language_val = data_dict["language"] if "language" in data_dict else ""
        self.assertEqual(language_val, "XX")
        control_points = data_dict["control_points"] if "control_points" in data_dict else []
        self.assertTrue(isinstance(control_points, list))
        hyw = next((cp for cp in control_points if isinstance(cp, dict) and "code" in cp and cp["code"] == "HYW"), {})
        self.assertTrue(isinstance(hyw, dict))
        hyw_dict = hyw if isinstance(hyw, dict) else {}
        hyw_arrival = hyw_dict["arrival"] if "arrival" in hyw_dict else ""
        self.assertEqual(hyw_arrival, "Normal (Generally less than 15 mins)")

    @patch("requests.get")
    def test_api_unavailable(self, mock_get):
        """
        Test handling of API unavailability by simulating a connection error.
        
        Args:
            mock_get: Mock object for the requests.get function to simulate API responses.
        """
        # Simulate API connection error
        mock_get.side_effect = Exception("Connection error")

        # Execute the tool
        result = self.tool.execute({"lang": "en"})

        # Check if the result is an error JSON
        self.assertEqual("type" in result and result["type"] or "", "Error")
        self.assertEqual("version" in result and result["version"] or "", "1.0")
        self.assertTrue("error" in result and "Connection error" in result["error"] or False)

    @patch("requests.get")
    def test_invalid_json_response(self, mock_get):
        """
        Test handling of invalid JSON response from the API.
        
        Args:
            mock_get: Mock object for the requests.get function to simulate API responses.
        """
        # Mock the response with invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        # Execute the tool
        result = self.tool.execute({"lang": "en"})

        # Check if the result is an error JSON
        self.assertEqual("type" in result and result["type"] or "", "Error")
        self.assertEqual("version" in result and result["version"] or "", "1.0")
        self.assertTrue("error" in result and "Invalid JSON" in result["error"] or False)

    @patch("requests.get")
    def test_empty_data_response(self, mock_get):
        """
        Test handling of an empty data response from the API.
        
        Args:
            mock_get: Mock object for the requests.get function to simulate API responses.
        """
        # Mock the response with empty data
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        # Execute the tool
        result = self.tool.execute({"lang": "en"})

        # Check if the result indicates no data
        self.assertTrue(isinstance(result, dict))
        result_dict = result if isinstance(result, dict) else {}
        type_val = result_dict["type"] if "type" in result_dict else ""
        version_val = result_dict["version"] if "version" in result_dict else ""
        self.assertEqual(type_val, "WaitTimes")
        self.assertEqual(version_val, "1.0")
        data = result_dict["data"] if "data" in result_dict else {}
        self.assertTrue(isinstance(data, dict))
        data_dict = data if isinstance(data, dict) else {}
        control_points = data_dict["control_points"] if "control_points" in data_dict else []
        self.assertTrue(isinstance(control_points, list))
        hyw = next((cp for cp in control_points if isinstance(cp, dict) and "code" in cp and cp["code"] == "HYW"), {})
        self.assertTrue(isinstance(hyw, dict))
        hyw_dict = hyw if isinstance(hyw, dict) else {}
        hyw_arrival = hyw_dict["arrival"] if "arrival" in hyw_dict else ""
        self.assertEqual(hyw_arrival, "Data not available")


if __name__ == "__main__":
    unittest.main()
