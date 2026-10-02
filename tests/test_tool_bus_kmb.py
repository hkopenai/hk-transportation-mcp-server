"""
Unit tests for the KMB bus route fetching tool.

The tool does `from hkopenai_common.json_utils import fetch_json_data`,
so the patch must target the local binding (`tools.bus_kmb.fetch_json_data`),
not `hkopenai_common.json_utils.fetch_json_data` -- patching the source module
attribute has no effect on the tool's locally-bound reference.
"""

import unittest
from unittest.mock import patch, MagicMock
from hkopenai.hk_transportation_mcp_server.tools.bus_kmb import _get_bus_kmb, register


class TestBusKMB(unittest.TestCase):
    """Tests for the KMB bus route fetching tool."""

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
        """Patch the local `fetch_json_data` binding in the tool module."""
        self.mock_fetch_json_data = patch(
            "hkopenai.hk_transportation_mcp_server.tools.bus_kmb.fetch_json_data"
        ).start()
        self.mock_fetch_json_data.return_value = self.API_RESPONSE
        self.addCleanup(patch.stopall)

    def test_get_bus_kmb_default_lang(self):
        """Test fetching bus routes with the default language (English)."""
        result = _get_bus_kmb()
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["route"], "1")
        self.assertEqual(result["data"][0]["bound"], "outbound")
        self.assertEqual(result["data"][0]["origin"], "CHUK YUEN ESTATE")
        self.assertEqual(result["data"][0]["destination"], "STAR FERRY")
        self.assertEqual(result["data"][1]["bound"], "inbound")

    def test_get_bus_kmb_tc_lang(self):
        """Test fetching bus routes with Traditional Chinese language."""
        result = _get_bus_kmb("tc")
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["origin"], "竹園邨")
        self.assertEqual(result["data"][0]["destination"], "尖沙咀碼頭")

    def test_get_bus_kmb_sc_lang(self):
        """Test fetching bus routes with Simplified Chinese language."""
        result = _get_bus_kmb("sc")
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["origin"], "竹园邨")
        self.assertEqual(result["data"][0]["destination"], "尖沙咀码头")

    def test_invalid_language_code(self):
        """Test that an invalid language code falls back to English."""
        result = _get_bus_kmb("xx")
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["origin"], "CHUK YUEN ESTATE")

    def test_api_unavailable(self):
        """Test that an upstream error is returned in the tool's Error envelope."""
        self.mock_fetch_json_data.return_value = {"error": "Connection error"}
        result = _get_bus_kmb()
        self.assertEqual(result["type"], "Error")
        self.assertIn("Connection error", result["error"])

    def test_invalid_json_response(self):
        """Test that a non-dict response returns an Error envelope."""
        self.mock_fetch_json_data.return_value = {"error": "Invalid JSON"}
        result = _get_bus_kmb()
        self.assertEqual(result["type"], "Error")
        self.assertIn("Invalid JSON", result["error"])

    def test_empty_data_response(self):
        """Test that an empty data list returns an empty RouteList."""
        self.mock_fetch_json_data.return_value = {
            "type": "RouteList",
            "version": "1.0",
            "generated_timestamp": "2025-06-12T21:32:34+08:00",
            "data": [],
        }
        result = _get_bus_kmb()
        self.assertEqual(result["type"], "RouteList")
        self.assertEqual(result["data"], [])

    def test_register_tool(self):
        """Test the registration of the get_bus_kmb tool with MCP server."""
        mock_mcp = MagicMock()
        register(mock_mcp)
        mock_mcp.tool.assert_called_once_with(
            description="All bus routes of Kowloon Motor Bus (KMB) and Long Win Bus Services Hong Kong. Data source: Kowloon Motor Bus and Long Win Bus Services"
        )
        mock_decorator = mock_mcp.tool.return_value
        mock_decorator.assert_called_once()
        decorated_function = mock_decorator.call_args[0][0]
        self.assertEqual(decorated_function.__name__, "get_bus_kmb")
        with patch(
            "hkopenai.hk_transportation_mcp_server.tools.bus_kmb._get_bus_kmb"
        ) as mock_get_bus_kmb:
            decorated_function(lang="en")
            mock_get_bus_kmb.assert_called_once_with("en")


if __name__ == "__main__":
    unittest.main()