"""Tool for fetching Land Boundary Control Points Waiting Time in Hong Kong."""

import requests
from mcp import Tool, Resource


class LandCustomWaitTimeTool(Tool):
    """
    A tool for fetching current waiting times at land boundary control points in Hong Kong.
    
    This class extends the base Tool class to provide functionality for retrieving
    and formatting wait time data from the Hong Kong Immigration Department API.
    """
    def __init__(self):
        super().__init__(
            name="get_land_boundary_wait_times",
            description="Fetch current waiting times at land boundary control points in Hong Kong.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lang": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": "en",
                        "description": "Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
                        "enum": ["en", "tc", "sc"],
                        "title": "Lang",
                    }
                },
            },
        )
        self.control_points = {
            "HYW": "Heung Yuen Wai",
            "HZM": "Hong Kong-Zhuhai-Macao Bridge",
            "LMC": "Lok Ma Chau",
            "LSC": "Lok Ma Chau Spur Line",
            "LWS": "Lo Wu",
            "MKT": "Man Kam To",
            "SBC": "Shenzhen Bay",
            "STK": "Sha Tau Kok",
        }
        self.status_codes = {
            0: "Normal (Generally less than 15 mins)",
            1: "Busy (Generally less than 30 mins)",
            2: "Very Busy (Generally 30 mins or above)",
            4: "System Under Maintenance",
            99: "Non Service Hours",
        }

    def execute(self, arguments):
        """
        Execute the tool to fetch waiting times based on provided arguments.
        
        Args:
            arguments (dict): A dictionary containing the input parameters, including 'lang' for language preference.
            
        Returns:
            dict: JSON-compatible dictionary containing the waiting times at various control points.
        """
        try:
            lang = arguments.get("lang", "en")
            url = "https://secure1.info.gov.hk/immd/mobileapps/2bb9ae17/data/CPQueueTimeR.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            result = self.format_wait_times(data, lang)
            return {"type": "WaitTimes", "data": result}
        except Exception as e:
            return {"type": "Error", "error": str(e)}

    def format_wait_times(self, data, lang):
        """
        Format the waiting time data into a JSON-compatible dictionary.
        
        Args:
            data (dict): The JSON data containing wait times for different control points.
            lang (str): The language code for formatting the output (en/tc/sc).
            
        Returns:
            dict: A dictionary listing wait times for arrival and departure at each control point.
        """
        wait_times = []
        for code, name in self.control_points.items():
            if code in data:
                arr_status = data[code].get("arrQueue", 99)
                dep_status = data[code].get("depQueue", 99)
                arr_desc = self.status_codes.get(arr_status, "Unknown")
                dep_desc = self.status_codes.get(dep_status, "Unknown")
                wait_times.append({
                    "name": name,
                    "code": code,
                    "arrival": arr_desc,
                    "departure": dep_desc
                })
            else:
                wait_times.append({
                    "name": name,
                    "code": code,
                    "arrival": "Data not available",
                    "departure": "Data not available"
                })
        return {"language": lang.upper(), "control_points": wait_times}


def register_tools():
    """
    Register the LandCustomWaitTimeTool for use in the MCP server.
    
    Returns:
        list: A list containing an instance of LandCustomWaitTimeTool.
    """
    return [LandCustomWaitTimeTool()]
