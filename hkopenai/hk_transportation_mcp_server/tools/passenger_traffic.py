"""
Module for fetching passenger traffic statistics at Hong Kong control points.

This module provides functionality to retrieve and process daily passenger traffic data
from the Hong Kong Immigration Department, including breakdowns by resident type and date range.
"""

from typing import List, Dict, Optional, Union, Annotated
from datetime import datetime, timedelta
from pydantic import Field
from hkopenai_common.csv_utils import fetch_csv_from_url


def register(mcp):
    """Registers the get_passenger_stats tool with the MCP server."""

    @mcp.tool(
        description="The statistics on daily passenger traffic provides figures concerning daily statistics on inbound and outbound passenger trips at all control points since 2021 (with breakdown by Hong Kong Residents, Mainland Visitors and Other Visitors). Return last 7 days data if no date range is specified."
    )
    def get_passenger_stats(
        start_date: Annotated[
            Optional[str], Field(description="Start date in DD-MM-YYYY format")
        ] = None,
        end_date: Annotated[
            Optional[str], Field(description="End date in DD-MM-YYYY format")
        ] = None,
    ) -> Dict:
        """Get passenger traffic statistics."""
        return _get_passenger_stats(start_date, end_date)





def _get_passenger_stats(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict:
    """Get passenger traffic statistics"""
    url = "https://www.immd.gov.hk/opendata/eng/transport/immigration_clearance/statistics_on_daily_passenger_traffic.csv"
    data = fetch_csv_from_url(url, encoding="utf-8-sig")

    if "error" in data:
        return {"type": "Error", "error": data["error"]}

    # Get last 7 days if no dates specified (including today)
    if not start_date and not end_date:
        end_date = datetime.now().strftime("%d-%m-%Y")
        start_date = (datetime.now() - timedelta(days=6)).strftime("%d-%m-%Y")

    # Read all data first
    all_data = []
    for row in data:
        # Handle both 'Date' and '\ufeffDate' from BOM
        date_key = "Date" if "Date" in row else "\ufeffDate"
        if date_key not in row:
            continue
        current_date = row[date_key]
        current_dt = datetime.strptime(current_date, "%d-%m-%Y")
        all_data.append(
            {
                "dt": current_dt,
                "data": {
                    "date": current_date,
                    "control_point": row["Control Point"],
                    "direction": row["Arrival / Departure"],
                    "hk_residents": int(row["Hong Kong Residents"]),
                    "mainland_visitors": int(row["Mainland Visitors"]),
                    "other_visitors": int(row["Other Visitors"]),
                    "total": int(row["Total"]),
                },
            }
        )

    # Filter by date range
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%d-%m-%Y")
        except ValueError:
            return {
                "type": "Error",
                "error": "Invalid date format for start_date. Use DD-MM-YYYY",
            }
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%d-%m-%Y")
        except ValueError:
            return {
                "type": "Error",
                "error": "Invalid date format for end_date. Use DD-MM-YYYY",
            }

    filtered_data = []
    for item in all_data:
        if start_dt and item["dt"] < start_dt:
            continue
        if end_dt and item["dt"] > end_dt:
            continue
        filtered_data.append(item)

    # Sort by date (newest first)
    filtered_data.sort(key=lambda x: x["dt"], reverse=True)

    # Extract just the data dictionaries
    results = [item["data"] for item in filtered_data]
    return {"type": "PassengerStats", "data": results}

