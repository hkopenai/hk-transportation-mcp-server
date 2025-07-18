"""
Unit tests for the Passenger Traffic Data fetching tool.

This module tests the functionality of fetching passenger traffic data from the API,
ensuring correct handling of date filters and error conditions.
"""

import unittest
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock
from hkopenai.hk_transportation_mcp_server.tools.passenger_traffic import (
    _get_passenger_stats,
    register,
)


class TestPassengerTraffic(unittest.TestCase):
    """
    Test class for verifying the functionality of the Passenger Traffic Data fetching tool.

    This class contains tests to ensure that the fetch_passenger_traffic_data function handles
    different date filters and error conditions appropriately.
    """

    CSV_DATA = """\ufeffDate,Control Point,Arrival / Departure,Hong Kong Residents,Mainland Visitors,Other Visitors,Total
01-01-2021,Airport,Arrival,341,0,9,350
01-01-2021,Airport,Departure,803,17,28,848
02-01-2021,Airport,Arrival,363,10,10,383
02-01-2021,Airport,Departure,940,22,33,995
03-01-2021,Airport,Arrival,880,4,36,920
03-01-2021,Airport,Departure,1146,31,44,1221
04-01-2021,Airport,Arrival,445,1,12,458
04-01-2021,Airport,Departure,455,2,41,498
05-01-2021,Airport,Arrival,500,5,15,520
05-01-2021,Airport,Departure,600,25,35,660
06-01-2021,Airport,Arrival,550,8,18,576
06-01-2021,Airport,Departure,700,30,40,770
07-01-2021,Airport,Arrival,600,10,20,630
07-01-2021,Airport,Departure,800,35,45,880
08-01-2021,Airport,Arrival,650,12,22,684
08-01-2021,Airport,Departure,850,40,50,940
"""

    def setUp(self):
        """
        Set up test fixtures before each test method.

        This method sets up mocks for the urllib.request.urlopen function and the get_current_date
        function to simulate API responses and control the date used in tests.
        """
        self.mock_datetime_now = patch(
            "hkopenai.hk_transportation_mcp_server.tools.passenger_traffic.datetime"
        ).start()
        self.mock_datetime_now.return_value = datetime(
            2021, 1, 8
        )  # Matches latest date in test data

        self.addCleanup(patch.stopall)

    @patch("hkopenai_common.csv_utils.fetch_csv_from_url")
    def test_get_passenger_stats_default_lang(self, mock_fetch_csv_from_url):
        """
        Test fetching passenger traffic data with default parameters (last 7 days).

        Args:
            mock_fetch_csv_from_url: Mock object for the fetch_csv_from_url function to simulate API responses.
        """
        mock_fetch_csv_from_url.return_value = [dict(zip(self.CSV_DATA.splitlines()[0].split(','), row.split(','))) for row in self.CSV_DATA.splitlines()[1:]]

        result = _get_passenger_stats()

        # Should return last 7 days by default
        self.assertEqual(len(result["data"]), 14)  # 7 days * 2 directions
        self.assertEqual(
            result["data"][0],
            {
                "date": "08-01-2021",
                "control_point": "Airport",
                "direction": "Arrival",
                "hk_residents": 650,
                "mainland_visitors": 12,
                "other_visitors": 22,
                "total": 684,
            },
        )

    def test_start_date_filter(self):
        """
        Test fetching passenger traffic data with a specified start date.
        """
        with patch(
            "urllib.request.urlopen",
            return_value=mock_open(read_data=self.CSV_DATA.encode("utf-8"))(),
        ):
            result = _get_passenger_stats(start_date="03-01-2021")
            self.assertEqual(len(result["data"]), 12)  # 6 days * 2 directions
            self.assertEqual(result["data"][0]["date"], "08-01-2021")

    def test_end_date_filter(self):
        """
        Test fetching passenger traffic data with a specified end date.
        """
        with patch(
            "urllib.request.urlopen",
            return_value=mock_open(read_data=self.CSV_DATA.encode("utf-8"))(),
        ):
            result = _get_passenger_stats(end_date="03-01-2021")
            self.assertEqual(len(result["data"]), 6)  # 3 days * 2 directions
            self.assertEqual(result["data"][-1]["date"], "01-01-2021")

    def test_both_date_filters(self):
        """
        Test fetching passenger traffic data with both start and end date filters.
        """
        with patch(
            "urllib.request.urlopen",
            return_value=mock_open(read_data=self.CSV_DATA.encode("utf-8"))(),
        ):
            result = _get_passenger_stats(
                start_date="02-01-2021",
                end_date="04-01-2021",
            )
            self.assertEqual(len(result["data"]), 6)  # 3 days * 2 directions
            self.assertEqual(result["data"][0]["date"], "04-01-2021")
            self.assertEqual(result["data"][-1]["date"], "02-01-2021")

    def test_invalid_date_format(self):
        """
        Test handling of invalid date format in start and end date parameters.
        """
        with patch(
            "urllib.request.urlopen",
            return_value=mock_open(read_data=self.CSV_DATA.encode("utf-8"))(),
        ):
            result_start = _get_passenger_stats(start_date="2021-01-02")  # Wrong format
            self.assertTrue(isinstance(result_start, dict))
            result_start_dict = result_start if isinstance(result_start, dict) else {}
            type_val_start = result_start_dict.get("type", "")
            self.assertEqual(type_val_start, "Error")
            error_val_start = result_start_dict.get("error", "")
            self.assertTrue(
                "date format" in error_val_start.lower()
                or "invalid" in error_val_start.lower()
            )

            result_end = _get_passenger_stats(end_date="2021-01-02")  # Wrong format
            self.assertTrue(isinstance(result_end, dict))
            result_end_dict = result_end if isinstance(result_end, dict) else {}
            type_val_end = result_end_dict.get("type", "")
            self.assertEqual(type_val_end, "Error")
            error_val_end = result_end_dict.get("error", "")
            self.assertTrue(
                "date format" in error_val_end.lower()
                or "invalid" in error_val_end.lower()
            )

    def test_dates_out_of_range(self):
        """
        Test handling of date filters that are out of the available data range.
        """
        with patch(
            "urllib.request.urlopen",
            return_value=mock_open(read_data=self.CSV_DATA.encode("utf-8"))(),
        ):
            result = _get_passenger_stats(start_date="01-01-2020")  # Before data range
            self.assertEqual(len(result["data"]), 16)  # Should return all data
            result = _get_passenger_stats(end_date="01-01-2022")  # After data range
            self.assertEqual(len(result["data"]), 0)  # No data can be return

    def test_data_source_unavailable(self):
        """
        Test handling of API unavailability by simulating a connection error.
        """
        with patch("hkopenai_common.csv_utils.fetch_csv_from_url", return_value={"error": "Connection error"}):
            result = _get_passenger_stats()
            self.assertTrue(isinstance(result, dict))
            result_dict = result if isinstance(result, dict) else {}
            type_val = result_dict.get("type", "")
            self.assertEqual(type_val, "Error")
            error_val = result_dict.get("error", "")
            self.assertTrue("Connection error" in error_val)

    def test_malformed_csv_data(self):
        """
        Test handling of malformed CSV data from the API.
        """
        malformed_data = """\ufeffDate,Control Point,Arrival / Departure,Hong Kong Residents,Mainland Visitors,Other Visitors,Total
01-01-2021,Airport,Arrival,invalid,0,9,350
"""
        with patch("hkopenai_common.csv_utils.fetch_csv_from_url", return_value=[dict(zip(malformed_data.splitlines()[0].split(','), row.split(','))) for row in malformed_data.splitlines()[1:]]):
            result = _get_passenger_stats()
            self.assertTrue(isinstance(result, dict))
            result_dict = result if isinstance(result, dict) else {}
            type_val = result_dict.get("type", "")
            self.assertEqual(type_val, "Error")
            error_val = result_dict.get("error", "")
            self.assertTrue(
                "ValueError" in error_val or "malformed" in error_val.lower()
            )

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
