"""Tests for the Land Boundary Control Points Waiting Time tool."""

import unittest
from unittest.mock import patch, MagicMock
from hkopenai.hk_transportation_mcp_server.tools.land_custom_wait_time import (
    _get_land_boundary_wait_times,
    register,
)


class TestLandCustomWaitTimeTool(unittest.TestCase):
    """Tests for the land boundary control points waiting time tool."""

    def test_fetch_wait_times_en_language(self):
        """Test fetching wait times with English language."""
        with patch("requests.get") as mock_get:
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

            result = _fetch_wait_times("en")

            self.assertTrue(isinstance(result, dict))
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
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "HYW": {"arrQueue": 0, "depQueue": 0},
                "HZM": {"arrQueue": 1, "depQueue": 1},
            }
            mock_get.return_value = mock_response

            result = _fetch_wait_times("tc")

            self.assertTrue(isinstance(result, dict))
            self.assertEqual(result["type"], "WaitTimes")
            self.assertEqual(result["data"]["language"], "TC")
            hyw = next(
                (cp for cp in result["data"]["control_points"] if cp["code"] == "HYW"),
                {},
            )
            self.assertEqual(hyw["arrival"], "Normal (Generally less than 15 mins)")

    def test_fetch_wait_times_sc_language(self):
        """Test fetching wait times with Simplified Chinese language."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "HYW": {"arrQueue": 0, "depQueue": 0},
                "HZM": {"arrQueue": 1, "depQueue": 1},
            }
            mock_get.return_value = mock_response

            result = _fetch_wait_times("sc")

            self.assertTrue(isinstance(result, dict))
            self.assertEqual(result["type"], "WaitTimes")
            self.assertEqual(result["data"]["language"], "SC")
            hyw = next(
                (cp for cp in result["data"]["control_points"] if cp["code"] == "HYW"),
                {},
            )
            self.assertEqual(hyw["arrival"], "Normal (Generally less than 15 mins)")

    def test_invalid_language_code(self):
        """Test handling of invalid language codes."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"HYW": {"arrQueue": 0, "depQueue": 0}}
            mock_get.return_value = mock_response
            _ = mock_get  # Added to satisfy pylint W0612

            result = _fetch_wait_times("xx")

            self.assertTrue(isinstance(result, dict))
            self.assertEqual(result["type"], "WaitTimes")
            self.assertEqual(result["data"]["language"], "XX")
            hyw = next(
                (cp for cp in result["data"]["control_points"] if cp["code"] == "HYW"),
                {},
            )
            self.assertEqual(hyw["arrival"], "Normal (Generally less than 15 mins)")

    def test_api_unavailable(self):
        """Test behavior when the API is unavailable."""
        with patch(
            "requests.get", side_effect=Exception("Connection error")
        ) as mock_get:
            result = _fetch_wait_times("en")
            self.assertEqual(result["type"], "Error")
            self.assertTrue("Connection error" in result["error"])

    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses from the API."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response

            result = _fetch_wait_times("en")
            self.assertEqual(result["type"], "Error")
            self.assertTrue("Invalid JSON" in result["error"])

    def test_empty_data_response(self):
        """Test handling of empty data responses from the API."""
        with patch("hkopenai_common.json_utils.fetch_json_data", return_value={}):
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
