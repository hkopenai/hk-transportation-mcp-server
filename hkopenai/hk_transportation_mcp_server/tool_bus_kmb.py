"""
Module for fetching bus route data for Kowloon Motor Bus (KMB) and Long Win Bus Services in Hong Kong.

This module provides functionality to retrieve and format bus route information from the KMB API,
supporting multiple languages for user accessibility.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Union
from pydantic import Field
from typing_extensions import Annotated


def fetch_bus_routes(lang: str = "en") -> Union[List[Dict], Dict]:
    """Fetch all KMB/LWB bus routes from the API

    Args:
        lang: Language code (en/tc/sc) for responses

    Returns:
        List of route dictionaries with route details or a dictionary with error information
    """
    try:
        url = "https://data.etabus.gov.hk/v1/transport/kmb/route/"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode("utf-8"))

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

        return filtered_routes
    except urllib.error.URLError as e:
        return {"type": "Error", "error": f"Connection error: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"type": "Error", "error": f"Invalid JSON response: {str(e)}"}
    except Exception as e:
        return {"type": "Error", "error": str(e)}


def get_bus_kmb(
    lang: Annotated[
        Optional[str],
        Field(
            description="Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
            json_schema_extra={"enum": ["en", "tc", "sc"]},
        ),
    ] = "en",
) -> Dict:
    """Get all bus routes of Kowloon Motor Bus (KMB) and Long Win Bus Services Hong Kong"""
    result = fetch_bus_routes(lang if lang else "en")
    if isinstance(result, dict) and result.get("type") == "Error":
        return result
    return {"type": "RouteList", "data": result}
