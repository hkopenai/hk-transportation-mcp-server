"""
Module for fetching bus route data for Kowloon Motor Bus (KMB) and Long Win Bus Services in Hong Kong.

This module provides functionality to retrieve and format bus route information from the KMB API,
supporting multiple languages for user accessibility.
"""

from typing import Dict, List, Optional, Union
from pydantic import Field
from typing_extensions import Annotated
from hkopenai_common.json_utils import fetch_json_data


def register(mcp):
    """Registers the get_bus_kmb tool with the MCP server."""

    @mcp.tool(
        description="All bus routes of Kowloon Motor Bus (KMB) and Long Win Bus Services Hong Kong. Data source: Kowloon Motor Bus and Long Win Bus Services"
    )
    def get_bus_kmb(
        lang: Annotated[
            Optional[str],
            Field(
                description="Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
                json_schema_extra={"enum": ["en", "tc", "sc"]},
            ),
        ] = "en",
    ) -> Dict:
        return _get_bus_kmb(lang)





def _get_bus_kmb(
    lang: Annotated[
        Optional[str],
        Field(
            description="Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
            json_schema_extra={"enum": ["en", "tc", "sc"]},
        ),
    ] = "en",
) -> Dict:
    """Get all bus routes of Kowloon Motor Bus (KMB) and Long Win Bus Services Hong Kong"""
    url = "https://data.etabus.gov.hk/v1/transport/kmb/route/"
    data = fetch_json_data(url)

    if "error" in data:
        return {"type": "Error", "error": data["error"]}

    # Validate language code, default to 'en' if invalid
    valid_langs = ["en", "tc", "sc"]
    if lang not in valid_langs:
        lang = "en"

    # Filter fields based on language
    filtered_routes = []
    for route in data["data"]:
        filtered_routes.append(
            {
                "route": route["route"],
                "bound": "outbound" if route["bound"] == "O" else "inbound",
                "service_type": route["service_type"],
                "origin": route[f"orig_{lang}"],
                "destination": route[f"dest_{lang}"],
            }
        )

    return {"type": "RouteList", "data": filtered_routes}
