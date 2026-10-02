"""
Unit tests for the transport snapshot aggregator.

The aggregator calls the two per-section helpers directly (no network
calls) and packages their dict outputs. Tests patch the helpers in
the aggregator's namespace (transport_snapshot.passenger_traffic and
transport_snapshot.land_custom_wait_time) so the imports inside the
aggregator are intercepted.
"""

import unittest
from unittest.mock import patch

from hkopenai.hk_transportation_mcp_server.tools.transport_snapshot import (
    _get_transport_snapshot,
    register,
)


WAIT_PAYLOAD = {
    "type": "WaitTimes",
    "data": {
        "language": "EN",
        "control_points": [
            {"name": "Lo Wu", "code": "LWS", "arrival": "Normal", "departure": "Normal"},
        ],
    },
}

PAX_PAYLOAD = {
    "type": "PassengerStats",
    "data": [
        {
            "date": "08-01-2021",
            "control_point": "Airport",
            "direction": "Arrival",
            "hk_residents": 650,
            "mainland_visitors": 12,
            "other_visitors": 22,
            "total": 684,
        },
    ],
}


class TestTransportSnapshot(unittest.TestCase):
    """Tests for the transport snapshot aggregator."""

    @patch(
        "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot.passenger_traffic"
    )
    @patch(
        "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot.land_custom_wait_time"
    )
    def test_happy_path(self, mock_wait_mod, mock_pax_mod):
        """Both sections return non-error envelopes -> both surface in payload."""
        mock_wait_mod._get_land_boundary_wait_times.return_value = WAIT_PAYLOAD
        mock_pax_mod._get_passenger_stats.return_value = PAX_PAYLOAD

        result = _get_transport_snapshot()

        self.assertEqual(result["type"], "TransportSnapshot")
        data = result["data"]
        self.assertEqual(data["land_boundary_wait_times"], WAIT_PAYLOAD)
        self.assertEqual(data["passenger_traffic"], PAX_PAYLOAD)

        meta = data["_meta"]
        self.assertIn("generated_at", meta)
        self.assertEqual(
            set(meta["sections"]),
            {"land_boundary_wait_times", "passenger_traffic"},
        )
        # Sources are listed for both sections.
        self.assertIn("land_boundary_wait_times", meta["sources"])
        self.assertIn("passenger_traffic", meta["sources"])

        # Args are forwarded to the per-section helpers.
        mock_wait_mod._get_land_boundary_wait_times.assert_called_once_with("en")
        mock_pax_mod._get_passenger_stats.assert_called_once_with(None, None)

    @patch(
        "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot.passenger_traffic"
    )
    @patch(
        "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot.land_custom_wait_time"
    )
    def test_args_forwarded(self, mock_wait_mod, mock_pax_mod):
        """Caller-supplied lang/start_date/end_date are passed through."""
        mock_wait_mod._get_land_boundary_wait_times.return_value = WAIT_PAYLOAD
        mock_pax_mod._get_passenger_stats.return_value = PAX_PAYLOAD

        _get_transport_snapshot(lang="tc", start_date="01-01-2024", end_date="07-01-2024")

        mock_wait_mod._get_land_boundary_wait_times.assert_called_once_with("tc")
        mock_pax_mod._get_passenger_stats.assert_called_once_with(
            "01-01-2024", "07-01-2024"
        )

    @patch(
        "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot.passenger_traffic"
    )
    @patch(
        "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot.land_custom_wait_time"
    )
    def test_land_boundary_failure_does_not_break_passenger_traffic(
        self, mock_wait_mod, mock_pax_mod
    ):
        """If wait_times returns an Error envelope, the other section still surfaces."""
        error = {"type": "Error", "error": "Connection error"}
        mock_wait_mod._get_land_boundary_wait_times.return_value = error
        mock_pax_mod._get_passenger_stats.return_value = PAX_PAYLOAD

        result = _get_transport_snapshot()
        self.assertEqual(result["data"]["land_boundary_wait_times"], error)
        self.assertEqual(result["data"]["passenger_traffic"], PAX_PAYLOAD)

    @patch(
        "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot.passenger_traffic"
    )
    @patch(
        "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot.land_custom_wait_time"
    )
    def test_passenger_traffic_failure_does_not_break_wait_times(
        self, mock_wait_mod, mock_pax_mod
    ):
        """If passenger_traffic returns an Error envelope, wait_times still surfaces."""
        error = {"type": "Error", "error": "CSV parse error"}
        mock_wait_mod._get_land_boundary_wait_times.return_value = WAIT_PAYLOAD
        mock_pax_mod._get_passenger_stats.return_value = error

        result = _get_transport_snapshot()
        self.assertEqual(result["data"]["land_boundary_wait_times"], WAIT_PAYLOAD)
        self.assertEqual(result["data"]["passenger_traffic"], error)

    def test_register_tool(self):
        """Register wires up the get_transport_snapshot MCP tool."""
        from unittest.mock import MagicMock

        mock_mcp = MagicMock()
        register(mock_mcp)
        mock_mcp.tool.assert_called_once()
        mock_decorator = mock_mcp.tool.return_value
        mock_decorator.assert_called_once()
        decorated_function = mock_decorator.call_args[0][0]
        self.assertEqual(decorated_function.__name__, "get_transport_snapshot")
        with patch(
            "hkopenai.hk_transportation_mcp_server.tools.transport_snapshot._get_transport_snapshot"
        ) as mock_snapshot:
            decorated_function(lang="en")
            mock_snapshot.assert_called_once_with(
                lang="en", start_date=None, end_date=None
            )


if __name__ == "__main__":
    unittest.main()