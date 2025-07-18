"""
Unit tests for the KMB bus route fetching tool.

This module tests the functionality of fetching bus route data from the KMB API,
ensuring correct handling of language preferences and error conditions.
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from hkopenai.hk_transportation_mcp_server.tools.bus_kmb import _get_bus_kmb, register


class TestBusKMB(unittest.TestCase):
    """
    Test class for verifying the functionality of the KMB bus route fetching tool.

    This class contains tests to ensure that the fetch_bus_routes function handles
    different language inputs and error conditions appropriately.
    """

    API_RESPONSE = {
        "type": "RouteList",
        "version": "1.0",
        "generated_timestamp": "2025-06-12T21:32:34+08:00",
        "data": [
            {
                "route": "1",
                "bound": "O",
                "service_type": "1",
                "orig_en": "CHUK YUEN ESTATE",
                "orig_tc": "竹園邨",
                "orig_sc": "竹园邨",
                "dest_en": "STAR FERRY",
                "dest_tc": "尖沙咀碼頭",
                "dest_sc": "尖沙咀码头",
            },
            {
                "route": "1",
                "bound": "I",
                "service_type": "1",
                "orig_en": "STAR FERRY",
                "orig_tc": "尖沙咀碼頭",
                "orig_sc": "尖沙咀码头",
                "dest_en": "CHUK YUEN ESTATE",
                "dest_tc": "竹園邨",
                "dest_sc": "竹园邨",
            },
        ],
    }

    def setUp(self):
        """
        Set up test fixtures before each test method.

        This method sets up a mock for the urllib.request.urlopen function to simulate
        API responses for bus route data.
        """
        self.mock_fetch_json_data = patch("hkopenai_common.json_utils.fetch_json_data").start()
        self.mock_fetch_json_data.return_value = self.API_RESPONSE
        self.addCleanup(patch.stopall)

    def test_get_bus_kmb_default_lang(self):
        """
        Test fetching bus routes with the default language (English).
        """
        result = _get_bus_kmb()
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["route"], "1")
        self.assertEqual(result["data"][0]["bound"], "outbound")
        self.assertEqual(result["data"][0]["origin"], "CHUK YUEN ESTATE")
        self.assertEqual(result["data"][0]["destination"], "STAR FERRY")
        self.assertEqual(result["data"][1]["bound"], "inbound")

    def test_get_bus_kmb_tc_lang(self):
        """
        Test fetching bus routes with Traditional Chinese language.
        """
        result = _get_bus_kmb("tc")
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["origin"], "竹園邨")
        self.assertEqual(result["data"][0]["destination"], "尖沙咀碼頭")

    def test_get_bus_kmb_sc_lang(self):
        """
        Test fetching bus routes with Simplified Chinese language.
        """
        result = _get_bus_kmb("sc")
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["origin"], "竹园邨")
        self.assertEqual(result["data"][0]["destination"], "尖沙咀码头")

    def test_invalid_language_code(self):
        """
        Test fetching bus routes with an invalid language code, expecting default to English.
        """
        result = _get_bus_kmb("xx")  # Invalid language code
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(
            result["data"][0]["origin"], "CHUK YUEN ESTATE"
        )  # Should default to English

    def test_api_unavailable(self):
        """
        Test handling of API unavailability by simulating a connection error.
        """
        with patch("urllib.request.urlopen", side_effect=Exception("Connection error")):
            result = _get_bus_kmb()
            self.assertTrue(isinstance(result, dict))
            result_dict = result if isinstance(result, dict) else {}
            type_val = result_dict.get("type", "")
            self.assertEqual(type_val, "Error")
            error_val = result_dict.get("error", "")
            self.assertTrue("Connection error" in error_val)

    def test_invalid_json_response(self):
        """
        Test handling of invalid JSON response from the API.
        """
        with patch("hkopenai_common.json_utils.fetch_json_data", return_value={"error": "Invalid JSON"}):
            result = _get_bus_kmb()
            self.assertTrue(isinstance(result, dict))
            result_dict = result if isinstance(result, dict) else {}
            type_val = result_dict.get("type", "")
            self.assertEqual(type_val, "Error")
            error_val = result_dict.get("error", "")
            self.assertTrue("Invalid JSON" in error_val)

    def test_empty_data_response(self):
        """
        Test handling of an empty data response from the API.
        """
        empty_response = {
            "type": "RouteList",
            "version": "1.0",
            "generated_timestamp": "2025-06-12T21:32:34+08:00",
            "data": [],
        }
        with patch("hkopenai_common.json_utils.fetch_json_data", return_value=empty_response):
            result = _get_bus_kmb()
            self.assertEqual(len(result["data"]), 0)

    def test_register_tool(self):
        """
        Test the registration of the get_bus_kmb tool.
        """
        mock_mcp = MagicMock()

        # Call the register function
        register(mock_mcp)

        # Verify that mcp.tool was called with the correct description
        mock_mcp.tool.assert_called_once_with(
            description="All bus routes of Kowloon Motor Bus (KMB) and Long Win Bus Services Hong Kong. Data source: Kowloon Motor Bus and Long Win Bus Services"
        )

        # Get the mock that represents the decorator returned by mcp.tool
        mock_decorator = mock_mcp.tool.return_value

        # Verify that the mock decorator was called once (i.e., the function was decorated)
        mock_decorator.assert_called_once()

        # The decorated function is the first argument of the first call to the mock_decorator
        decorated_function = mock_decorator.call_args[0][0]

        # Verify the name of the decorated function
        self.assertEqual(decorated_function.__name__, "get_bus_kmb")

        # Call the decorated function and verify it calls _get_bus_kmb
        with patch(
            "hkopenai.hk_transportation_mcp_server.tools.bus_kmb._get_bus_kmb"
        ) as mock_get_bus_kmb:
            decorated_function(lang="en")
            mock_get_bus_kmb.assert_called_once_with("en")


if __name__ == "__main__":
    unittest.main()
