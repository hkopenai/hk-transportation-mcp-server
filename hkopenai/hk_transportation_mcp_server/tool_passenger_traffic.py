"""
Module for fetching passenger traffic statistics at Hong Kong control points.

This module provides functionality to retrieve and process daily passenger traffic data
from the Hong Kong Immigration Department, including breakdowns by resident type and date range.
"""

import csv
import urllib.request
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta


def get_current_date() -> datetime:
    """Wrapper for datetime.now() to allow mocking in tests"""
    return datetime.now()


def fetch_passenger_traffic_data(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Union[List[Dict], Dict]:
    """Fetch and parse passenger traffic data from Immigration Department

    Args:
        start_date: Optional start date in DD-MM-YYYY format
        end_date: Optional end date in DD-MM-YYYY format

    Returns:
        List of passenger traffic data with date, control_point, direction,
        hk_residents, mainland_visitors, other_visitors, total, or a dictionary
        containing error information.
    """
    try:
        url = "https://www.immd.gov.hk/opendata/eng/transport/immigration_clearance/statistics_on_daily_passenger_traffic.csv"
        response = urllib.request.urlopen(url)
        lines = [
            l.decode("utf-8-sig") for l in response.readlines()
        ]  # Use utf-8-sig to handle BOM
        reader = csv.DictReader(lines)

        # Get last 7 days if no dates specified (including today)
        if not start_date and not end_date:
            end_date = get_current_date().strftime("%d-%m-%Y")
            start_date = (get_current_date() - timedelta(days=6)).strftime("%d-%m-%Y")

        # Read all data first
        all_data = []
        for row in reader:
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
                return {"type": "Error", "version": "1.0", "error": "Invalid date format for start_date. Use DD-MM-YYYY"}
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%d-%m-%Y")
            except ValueError:
                return {"type": "Error", "version": "1.0", "error": "Invalid date format for end_date. Use DD-MM-YYYY"}

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
        return results
    except ValueError as e:
        return {"type": "Error", "version": "1.0", "error": f"ValueError: Malformed data - {str(e)}"}
    except Exception as e:
        return {"type": "Error", "version": "1.0", "error": f"Connection error: {str(e)}"}


def get_passenger_stats(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict:
    """Get passenger traffic statistics"""
    result = fetch_passenger_traffic_data(start_date, end_date)
    if isinstance(result, dict) and result.get("type") == "Error":
        return result
    return {"type": "PassengerStats", "version": "1.0", "data": result}
