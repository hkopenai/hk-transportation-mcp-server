"""Tool for fetching Land Boundary Control Points Waiting Time in Hong Kong."""

from typing import Dict, Annotated, Optional
from pydantic import Field
from hkopenai_common.json_utils import fetch_json_data


def register(mcp):
    """Register the get_land_boundary_wait_times tool with the MCP server."""

    @mcp.tool(
        description="Fetch current waiting times at land boundary control points in Hong Kong."
    )
    def get_land_boundary_wait_times(
        lang: Annotated[
            Optional[str],
            Field(
                description="Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
                json_schema_extra={"enum": ["en", "tc", "sc"]},
            ),
        ] = "en",
    ) -> Dict:
        """Get current waiting times at land boundary control points in Hong Kong."""
        return _get_land_boundary_wait_times(str(lang))


def _get_land_boundary_wait_times(lang: str) -> Dict:
    """Fetch land boundary control points waiting times."""
    control_points = {
        "HYW": "Heung Yuen Wai",
        "HZM": "Hong Kong-Zhuhai-Macao Bridge",
        "LMC": "Lok Ma Chau",
        "LSC": "Lok Ma Chau Spur Line",
        "LWS": "Lo Wu",
        "MKT": "Man Kam To",
        "SBC": "Shenzhen Bay",
        "STK": "Sha Tau Kok",
    }
    status_codes = {
        0: "Normal (Generally less than 15 mins)",
        1: "Busy (Generally less than 30 mins)",
        2: "Very Busy (Generally 30 mins or above)",
        4: "System Under Maintenance",
        99: "Non Service Hours",
    }
    url = "https://secure1.info.gov.hk/immd/mobileapps/2bb9ae17/data/CPQueueTimeR.json"
    data = fetch_json_data(url, timeout=10)

    if "error" in data:
        return {"type": "Error", "error": data["error"]}

    wait_times = []
    for code, name in control_points.items():
        if code in data:
            arr_status = data[code].get("arrQueue", 99)
            dep_status = data[code].get("depQueue", 99)
            arr_desc = status_codes.get(arr_status, "Unknown")
            dep_desc = status_codes.get(dep_status, "Unknown")
            wait_times.append(
                {
                    "name": name,
                    "code": code,
                    "arrival": arr_desc,
                    "departure": dep_desc,
                }
            )
        else:
            wait_times.append(
                {
                    "name": name,
                    "code": code,
                    "arrival": "Data not available",
                    "departure": "Data not available",
                }
            )
    return {
        "type": "WaitTimes",
        "data": {"language": lang.upper(), "control_points": wait_times},
    }



