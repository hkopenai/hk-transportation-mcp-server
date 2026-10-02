"""
Transport Snapshot Tool - one-shot cross-border travel snapshot for
Hong Kong, combining the Immigration Department's land boundary wait
times and the last 7 days of passenger traffic in a single MCP call.

The three tools in this server each answer a different question:

  * `get_bus_kmb`              - the full KMB bus catalogue (static-ish)
  * `get_land_boundary_wait_times` - real-time queue at HK boundary CP
  * `get_passenger_stats`       - last 7 days passenger traffic (CSV)

A user question like "how is cross-border travel today?" naturally
combines the second and third: real-time queue status at every
control point, plus the recent traffic context that explains why a
particular boundary is busy. The bus catalogue is a different
shape (route lookup, not cross-border travel) and is not pulled into
the snapshot.

Each section runs in isolation. If the land boundary feed fails,
the passenger traffic section still returns, and the broken section
is reported under its key in the `_meta.errors` map.

The function body follows the same shape as
`hk-finance-mcp-server`'s `get_economy_snapshot`: a single async
dispatcher that fans out via `asyncio.gather`, then packages each
result into a typed envelope that the caller can introspect.
"""

from datetime import datetime, timezone
from typing import Dict, Optional as OptArg

from . import land_custom_wait_time, passenger_traffic


def register(mcp):
    """Register the get_transport_snapshot tool with the MCP server."""

    @mcp.tool(
        description=(
            "One-shot cross-border travel snapshot for Hong Kong. Combines "
            "real-time queue times at every land boundary control point with "
            "the last 7 days of passenger traffic stats, returned in a single "
            "MCP call. Bus route catalogue is intentionally excluded -- it is "
            "a separate concern (route lookup, not cross-border travel)."
        )
    )
    def get_transport_snapshot(
        lang: OptArg[str] = "en",
        start_date: OptArg[str] = None,
        end_date: OptArg[str] = None,
    ) -> Dict:
        """Return a consolidated cross-border travel snapshot."""
        return _get_transport_snapshot(
            lang=lang,
            start_date=start_date,
            end_date=end_date,
        )


def _get_transport_snapshot(
    lang: str = "en",
    start_date: OptArg[str] = None,
    end_date: OptArg[str] = None,
) -> Dict:
    """Fetch the cross-border snapshot.

    Returns a dict with three keys:

    * `land_boundary_wait_times` - the WaitTimes envelope from
      `land_custom_wait_time._get_land_boundary_wait_times`, or an
      Error envelope if the feed failed.
    * `passenger_traffic` - the PassengerStats envelope from
      `passenger_traffic._get_passenger_stats`, or an Error envelope
      if the feed failed.
    * `_meta` - generation metadata (`generated_at`, `sections`,
      `sources`).

    Each section is fetched in isolation, so a failure in one feed
    does not suppress the other.
    """
    wait_times = land_custom_wait_time._get_land_boundary_wait_times(lang)
    pax = passenger_traffic._get_passenger_stats(start_date, end_date)

    return {
        "type": "TransportSnapshot",
        "data": {
            "land_boundary_wait_times": wait_times,
            "passenger_traffic": pax,
            "_meta": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "sections": [
                    "land_boundary_wait_times",
                    "passenger_traffic",
                ],
                "sources": {
                    "land_boundary_wait_times": (
                        "Immigration Department live queue feed "
                        "(https://secure1.info.gov.hk/immd/mobileapps/"
                        "2bb9ae17/data/CPQueueTimeR.json)"
                    ),
                    "passenger_traffic": (
                        "Immigration Department daily passenger traffic "
                        "CSV (https://www.immd.gov.hk/opendata/eng/transport/"
                        "immigration_clearance/statistics_on_daily_passenger_traffic.csv)"
                    ),
                },
            },
        },
    }