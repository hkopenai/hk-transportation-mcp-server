"""Tests for the Land Boundary Control Points Waiting Time tool.

The tool does `from hkopenai_common.json_utils import fetch_json_data`, so
the patch must target the local binding (`tools.land_custom_wait_time.fetch_json_data`).
The earlier version of this test file called a non-existent helper named
`_fetch_wait_times`; that was wrong -- the real helper is
`_get_land_boundary_wait_times`.
"""

import unittest
from unittest.mock import patch, MagicMock
from hkopenai.hk_transportation_mcp_server.tools.land_custom_wait_time import (
    _get_land_boundary_wait_times,
    register,
)


WAIT_DATA = {
    "HYW": {"arrQueue": 0, "depQueue": 0},
    "HZM": {"arrQueue": 1, "depQueue": 1},
    "LMC": {"arrQueue": 2, "depQueue": 2},
    "LSC": {"arrQueue": 0, "depQueue": 0},
    "LWS": {"arrQueue": 0, "depQueue": 0},
    "MKT": {"arrQueue": 0, "depQueue": 0},
    "SBC": {"arrQueue": 0, "depQueue": 0},
    "STK": {"arrQueue": 99, "depQueue": 99},
}


class TestLandCustomWaitTimeTool(unittest.TestCase):
    """Tests for the land boundary control points waiting time tool."""

    def setUp(self):
        """Patch the local `fetch_json_data` binding in the tool module."""
        self.mock_fetch_json_data = patch(
            "hkopenai.hk_transportation_mcp_server.tools.land_custom_wait_time.fetch_json_data"
        ).start()
        self.mock_fetch_json_data.return_value = WAIT_DATA
        self.addCleanup(patch.stopall)

    def test_fetch_wait_times_en_language(self):
        """Test fetching wait times with English language."""
        result = _get_land_boundary_wait_times("en")
        self.assertEqual(result["type"], "WaitTimes")
        self.assertEqual(result["data"]["language"], "EN")
        hyw = next(
            (cp for cp in result["data"]["control_points"] if cp["code"] == "HYW"),
            {},
        )
        stk = next(
            (cp for cp in result["data"]["control_points"] if cp["code"] == "STK"),
            {},
        )
        self.assertEqual(hyw["arrival"], "Normal (Generally less than 15 mins)")
        self.assertEqual(stk["arrival"], "Non Service Hours")

    def test_fetch_wait_times_tc_language(self):
        """Test fetching wait times with Traditional Chinese language."""
        result = _get_land_boundary_wait_times("tc")
        self.assertEqual(result["type"], "WaitTimes")
        self.assertEqual(result["data"]["language"], "TC")
        hyw = next(
            (cp for cp in result["data"]["control_points"] if cp["code"] == "HYW"),
            {},
        )
        self.assertEqual(hyw["arrival"], "Normal (Generally less than 15 mins)")

    def test_fetch_wait_times_sc_language(self):
        """Test fetching wait times with Simplified Chinese language."""
        result = _get_land_boundary_wait_times("sc")
        self.assertEqual(result["type"], "WaitTimes")
        self.assertEqual(result["data"]["language"], "SC")
        hyw = next(
            (cp for cp in result["data"]["control_points"] if cp["code"] == "HYW"),
            {},
        )
        self.assertEqual(hyw["arrival"], "Normal (Generally less than 15 mins)")

    def test_invalid_language_code(self):
        """Test that any language code is passed through verbatim."""
        result = _get_land_boundary_wait_times("xx")
        self.assertEqual(result["type"], "WaitTimes")
        self.assertEqual(result["data"]["language"], "XX")

    def test_api_unavailable(self):
        """Test that an upstream error is returned in the tool's Error envelope."""
        self.mock_fetch_json_data.return_value = {"error": "Connection error"}
        result = _get_land_boundary_wait_times("en")
        self.assertEqual(result["type"], "Error")
        self.assertIn("Connection error", result["error"])

    def test_invalid_json_response(self):
        """Test that a fetch_json_data error payload surfaces the wrapper error."""
        self.mock_fetch_json_data.return_value = {"error": "Invalid JSON"}
        result = _get_land_boundary_wait_times("en")
        self.assertEqual(result["type"], "Error")
        self.assertIn("Invalid JSON", result["error"])

    def test_empty_data_response(self):
        """Test that an empty response yields 'Data not available' for every control point."""
        self.mock_fetch_json_data.return_value = {}
        result = _get_land_boundary_wait_times("en")
        self.assertEqual(result["type"], "WaitTimes")
        self.assertEqual(len(result["data"]["control_points"]), 8)
        hyw = next(
            (cp for cp in result["data"]["control_points"] if cp["code"] == "HYW"),
            {},
        )
        self.assertEqual(hyw["arrival"], "Data not available")

    def test_register_tool(self):
        """Test the registration of the tool with MCP server."""
        mock_mcp = MagicMock()
        register(mock_mcp)
        mock_mcp.tool.assert_called_once_with(
            description="Fetch current waiting times at land boundary control points in Hong Kong."
        )
        mock_decorator = mock_mcp.tool.return_value
        mock_decorator.assert_called_once()
        decorated_function = mock_decorator.call_args[0][0]
        self.assertEqual(decorated_function.__name__, "get_land_boundary_wait_times")
        with patch(
            "hkopenai.hk_transportation_mcp_server.tools.land_custom_wait_time._get_land_boundary_wait_times"
        ) as mock_fetch_wait_times:
            decorated_function(lang="en")
            mock_fetch_wait_times.assert_called_once_with("en")


if __name__ == "__main__":
    unittest.main()