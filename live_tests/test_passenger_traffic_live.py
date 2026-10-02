"""Live integration test for the Immigration Department passenger-traffic feed.

Hits the real CSV endpoint
(https://www.immd.gov.hk/opendata/eng/transport/immigration_clearance/statistics_on_daily_passenger_traffic.csv)
and verifies the response shape. Skipped unless RUN_LIVE_TESTS=true is set,
and shares the throttle autouse fixture from ``conftest.py`` so a back-to-back
``pytest live_tests`` run does not trip the upstream rate-limiter.
"""

import os
import unittest

from hkopenai.hk_transportation_mcp_server.tools.passenger_traffic import (
    _get_passenger_stats,
)


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_TESTS") == "true",
    "set RUN_LIVE_TESTS=true to run live integration tests",
)
class TestPassengerTrafficLive(unittest.TestCase):
    """Live integration test against the Immigration Department feed."""

    def test_default_range_returns_passenger_stats_envelope(self):
        """A default query (no dates) should return the PassengerStats envelope."""
        result = _get_passenger_stats()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("type"), "PassengerStats")
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)
        self.assertTrue(
            len(result["data"]) > 0,
            "default range should yield at least one passenger record",
        )

    def test_each_row_has_required_fields(self):
        """Every row should expose the documented fields with sensible types."""
        result = _get_passenger_stats()
        self.assertEqual(result.get("type"), "PassengerStats")
        for row in result["data"]:
            self.assertIn("date", row)
            self.assertIsInstance(row["date"], str)
            self.assertIn("control_point", row)
            self.assertIsInstance(row["control_point"], str)
            self.assertTrue(row["control_point"], "control_point must not be empty")
            self.assertIn("direction", row)
            self.assertIn(row["direction"], ("Arrival", "Departure"))
            for int_field in (
                "hk_residents",
                "mainland_visitors",
                "other_visitors",
                "total",
            ):
                self.assertIn(int_field, row)
                self.assertIsInstance(row[int_field], int)
                self.assertGreaterEqual(row[int_field], 0)

    def test_explicit_date_range_is_honoured(self):
        """A explicit narrow range should return at least one record and respect the window."""
        result = _get_passenger_stats(start_date="01-01-2021", end_date="02-01-2021")
        self.assertEqual(result.get("type"), "PassengerStats")
        self.assertIsInstance(result["data"], list)
        # The CSV covers control points and Arrival/Departure, so even a single
        # day should yield multiple records.
        self.assertTrue(
            len(result["data"]) >= 1,
            "expected at least one record in 2021-01-01..2021-01-02",
        )
        for row in result["data"]:
            self.assertIn(row["date"][6:], ("2021",))  # year suffix of DD-MM-YYYY


if __name__ == "__main__":
    unittest.main()
