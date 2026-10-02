"""
Unit tests for the Passenger Traffic Data fetching tool.

The tool does `from hkopenai_common.csv_utils import fetch_csv_from_url`,
so the patch must target the local binding
(`tools.passenger_traffic.fetch_csv_from_url`), not
`hkopenai_common.csv_utils.fetch_csv_from_url` -- patching the source module
attribute has no effect on the tool's locally-bound reference.
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from hkopenai.hk_transportation_mcp_server.tools.passenger_traffic import (
    _get_passenger_stats,
    register,
)


CSV_DATA = """\ufeffDate,Control Point,Arrival / Departure,Hong Kong Residents,Mainland Visitors,Other Visitors,Total
01-01-2021,Airport,Arrival,341,0,9,350
01-01-2021,Airport,Departure,803,17,49,869
02-01-2021,Airport,Arrival,363,10,10,350
02-01-2021,Airport,Departure,940,22,55,1017
03-01-2021,Airport,Arrival,880,4,36,920
03-01-2021,Airport,Departure,1146,31,66,1243
04-01-2021,Airport,Arrival,445,1,12,458
04-01-2021,Airport,Departure,455,2,63,520
05-01-2021,Airport,Arrival,500,5,15,520
05-01-2021,Airport,Departure,600,25,57,682
06-01-2021,Airport,Arrival,550,8,18,576
06-01-2021,Airport,Departure,700,30,62,792
07-01-2021,Airport,Arrival,600,10,20,630
07-01-2021,Airport,Departure,800,35,67,902
08-01-2021,Airport,Arrival,650,12,22,684
08-01-2021,Airport,Departure,850,40,72,962
"""


def _parse_csv(csv_text):
    """Tiny CSV parser for tests (dict per row, BOM-stripped)."""
    rows_iter = csv_text.splitlines()
    header = [c.strip() for c in rows_iter[0].split(",")]
    rows = []
    for line in rows_iter[1:]:
        values = [v.strip() for v in line.split(",")]
        rows.append(dict(zip(header, values)))
    return rows


class TestPassengerTraffic(unittest.TestCase):
    """Tests for the Passenger Traffic Data fetching tool."""

    def setUp(self):
        """Patch the local `fetch_csv_from_url` binding in the tool module."""
        self.mock_fetch_csv_from_url = patch(
            "hkopenai.hk_transportation_mcp_server.tools.passenger_traffic.fetch_csv_from_url"
        ).start()
        self.mock_fetch_csv_from_url.return_value = _parse_csv(CSV_DATA)
        # Pin "now" so the default 7-day window resolves to the CSV's date range.
        self.mock_datetime_now = patch(
            "hkopenai.hk_transportation_mcp_server.tools.passenger_traffic.datetime"
        ).start()
        self.mock_datetime_now.now.return_value = datetime(2021, 1, 8)
        self.mock_datetime_now.strptime = datetime.strptime
        self.addCleanup(patch.stopall)

    def test_get_passenger_stats_default_window(self):
        """Default call (no dates) returns the last 7 days."""
        result = _get_passenger_stats()
        # 7 days * 2 directions = 14
        self.assertEqual(len(result["data"]), 14)
        self.assertEqual(result["data"][0]["date"], "08-01-2021")
        self.assertEqual(result["data"][0]["direction"], "Arrival")
        self.assertEqual(result["data"][0]["hk_residents"], 650)

    def test_start_date_filter(self):
        """Specifying only start_date filters from that date to the latest data."""
        result = _get_passenger_stats(start_date="03-01-2021")
        # 03 through 08 = 6 days * 2 directions = 12
        self.assertEqual(len(result["data"]), 12)
        self.assertEqual(result["data"][0]["date"], "08-01-2021")

    def test_end_date_filter(self):
        """Specifying only end_date filters from earliest data through that date."""
        result = _get_passenger_stats(end_date="03-01-2021")
        # 01 through 03 = 3 days * 2 directions = 6
        self.assertEqual(len(result["data"]), 6)
        self.assertEqual(result["data"][-1]["date"], "01-01-2021")

    def test_both_date_filters(self):
        """Specifying both dates returns only that range, newest first."""
        result = _get_passenger_stats(start_date="02-01-2021", end_date="04-01-2021")
        self.assertEqual(len(result["data"]), 6)
        self.assertEqual(result["data"][0]["date"], "04-01-2021")
        self.assertEqual(result["data"][-1]["date"], "02-01-2021")

    def test_invalid_date_format(self):
        """An invalid date string yields an Error envelope."""
        result = _get_passenger_stats(start_date="2021-01-02")  # wrong format
        self.assertEqual(result["type"], "Error")
        self.assertTrue("date format" in result["error"].lower())

        result_end = _get_passenger_stats(end_date="2021-01-02")
        self.assertEqual(result_end["type"], "Error")
        self.assertTrue("date format" in result_end["error"].lower())

    def test_dates_out_of_range(self):
        """A start_date before all data returns everything.

        The tool keeps items where `item.dt <= end_dt`, so an end_date
        after all data returns everything, not nothing. The earlier
        version of this test had the assertions reversed.
        """
        result = _get_passenger_stats(start_date="01-01-2020")
        # Before-data start -> all 16 rows returned.
        self.assertEqual(len(result["data"]), 16)
        # After-data end -> all rows are <= end_dt, so all 16 are kept.
        result = _get_passenger_stats(end_date="01-01-2022")
        self.assertEqual(len(result["data"]), 16)

    def test_data_source_unavailable(self):
        """A fetch_csv_from_url error payload surfaces the wrapper error."""
        self.mock_fetch_csv_from_url.return_value = {"error": "Connection error"}
        result = _get_passenger_stats()
        self.assertEqual(result["type"], "Error")
        self.assertIn("Connection error", result["error"])

    def test_malformed_csv_data(self):
        """Non-integer counts raise ValueError inside the tool and propagate.

        The current tool implementation does not wrap the int() conversion
        in a try/except, so a single bad cell raises before producing a
        result. Assert the propagation instead of expecting a wrapped
        Error envelope (which was the previous, broken expectation).
        """
        malformed = """\ufeffDate,Control Point,Arrival / Departure,Hong Kong Residents,Mainland Visitors,Other Visitors,Total
01-01-2021,Airport,Arrival,invalid,0,9,350
"""
        self.mock_fetch_csv_from_url.return_value = _parse_csv(malformed)
        with self.assertRaises(ValueError):
            _get_passenger_stats()

    def test_register_tool(self):
        """Test the registration of the tool with MCP server."""
        mock_mcp = MagicMock()
        register(mock_mcp)
        mock_mcp.tool.assert_called_once_with(
            description="The statistics on daily passenger traffic provides figures concerning daily statistics on inbound and outbound passenger trips at all control points since 2021 (with breakdown by Hong Kong Residents, Mainland Visitors and Other Visitors). Return last 7 days data if no date range is specified."
        )
        mock_decorator = mock_mcp.tool.return_value
        mock_decorator.assert_called_once()
        decorated_function = mock_decorator.call_args[0][0]
        self.assertEqual(decorated_function.__name__, "get_passenger_stats")
        with patch(
            "hkopenai.hk_transportation_mcp_server.tools.passenger_traffic._get_passenger_stats"
        ) as mock_get_passenger_stats:
            decorated_function(start_date="01-01-2023", end_date="31-01-2023")
            mock_get_passenger_stats.assert_called_once_with("01-01-2023", "31-01-2023")


if __name__ == "__main__":
    unittest.main()