"""Tool for fetching Land Boundary Control Points Waiting Time in Hong Kong."""

import requests
from mcp import Tool, Resource

class LandCustomWaitTimeTool(Tool):
    def __init__(self):
        super().__init__(
            name="get_land_boundary_wait_times",
            description="Fetch current waiting times at land boundary control points in Hong Kong.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lang": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "null"}
                        ],
                        "default": "en",
                        "description": "Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
                        "enum": ["en", "tc", "sc"],
                        "title": "Lang"
                    }
                }
            }
        )
        self.control_points = {
            "HYW": "Heung Yuen Wai",
            "HZM": "Hong Kong-Zhuhai-Macao Bridge",
            "LMC": "Lok Ma Chau",
            "LSC": "Lok Ma Chau Spur Line",
            "LWS": "Lo Wu",
            "MKT": "Man Kam To",
            "SBC": "Shenzhen Bay",
            "STK": "Sha Tau Kok"
        }
        self.status_codes = {
            0: "Normal (Generally less than 15 mins)",
            1: "Busy (Generally less than 30 mins)",
            2: "Very Busy (Generally 30 mins or above)",
            4: "System Under Maintenance",
            99: "Non Service Hours"
        }

    def execute(self, arguments):
        # Note: error_handler decorator removed due to import issue; error handling to be implemented manually if needed
        lang = arguments.get("lang", "en")
        url = "https://secure1.info.gov.hk/immd/mobileapps/2bb9ae17/data/CPQueueTimeR.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result = self.format_wait_times(data, lang)
        return result

    def format_wait_times(self, data, lang):
        formatted_result = f"Land Boundary Control Points Waiting Times ({lang.upper()}):\n\n"
        for code, name in self.control_points.items():
            if code in data:
                arr_status = data[code].get("arrQueue", 99)
                dep_status = data[code].get("depQueue", 99)
                arr_desc = self.status_codes.get(arr_status, "Unknown")
                dep_desc = self.status_codes.get(dep_status, "Unknown")
                formatted_result += f"{name} ({code}):\n"
                formatted_result += f"  Arrival: {arr_desc}\n"
                formatted_result += f"  Departure: {dep_desc}\n\n"
            else:
                formatted_result += f"{name} ({code}): Data not available\n\n"
        return formatted_result

def register_tools():
    return [LandCustomWaitTimeTool()]
