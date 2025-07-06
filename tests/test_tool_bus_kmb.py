"""
Unit tests for the KMB bus route fetching tool.

This module tests the functionality of fetching bus route data from the KMB API,
ensuring correct handling of language preferences and error conditions.
"""

import unittest
from unittest.mock import patch, mock_open
import json
from hkopenai.hk_transportation_mcp_server.tool_bus_kmb import fetch_bus_routes


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
        self.mock_urlopen = patch("urllib.request.urlopen").start()
        self.mock_urlopen.return_value = mock_open(
            read_data=json.dumps(self.API_RESPONSE).encode("utf-8")
        )()
        self.addCleanup(patch.stopall)

    def test_fetch_bus_routes_default_lang(self):
        """
        Test fetching bus routes with the default language (English).
        """
        result = fetch_bus_routes()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["route"], "1")
        self.assertEqual(result[0]["bound"], "outbound")
        self.assertEqual(result[0]["origin"], "CHUK YUEN ESTATE")
        self.assertEqual(result[0]["destination"], "STAR FERRY")
        self.assertEqual(result[1]["bound"], "inbound")

    def test_fetch_bus_routes_tc_lang(self):
        """
        Test fetching bus routes with Traditional Chinese language.
        """
        result = fetch_bus_routes("tc")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["origin"], "竹園邨")
        self.assertEqual(result[0]["destination"], "尖沙咀碼頭")

    def test_fetch_bus_routes_sc_lang(self):
        """
        Test fetching bus routes with Simplified Chinese language.
        """
        result = fetch_bus_routes("sc")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["origin"], "竹园邨")
        self.assertEqual(result[0]["destination"], "尖沙咀码头")

    def test_invalid_language_code(self):
        """
        Test fetching bus routes with an invalid language code, expecting default to English.
        """
        result = fetch_bus_routes("xx")  # Invalid language code
        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0]["origin"], "CHUK YUEN ESTATE"
        )  # Should default to English

    def test_api_unavailable(self):
        """
        Test handling of API unavailability by simulating a connection error.
        """
        with patch("urllib.request.urlopen", side_effect=Exception("Connection error")):
            result = fetch_bus_routes()
            self.assertTrue(isinstance(result, dict))
            result_dict = result if isinstance(result, dict) else {}
            type_val = result_dict.get("type", "")
            version_val = result_dict.get("version", "")
            self.assertEqual(type_val, "Error")
            self.assertEqual(version_val, "1.0")
            error_val = result_dict.get("error", "")
            self.assertTrue("Connection error" in error_val)

    def test_invalid_json_response(self):
        """
        Test handling of invalid JSON response from the API.
        """
        with patch(
            "urllib.request.urlopen",
            return_value=mock_open(read_data=b"Invalid JSON")(),
        ):
            result = fetch_bus_routes()
            self.assertTrue(isinstance(result, dict))
            result_dict = result if isinstance(result, dict) else {}
            type_val = result_dict.get("type", "")
            version_val = result_dict.get("version", "")
            self.assertEqual(type_val, "Error")
            self.assertEqual(version_val, "1.0")
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
        with patch(
            "urllib.request.urlopen",
            return_value=mock_open(
                read_data=json.dumps(empty_response).encode("utf-8")
            )(),
        ):
            result = fetch_bus_routes()
            self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
