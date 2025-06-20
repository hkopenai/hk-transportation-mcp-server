import json
import urllib.request
from typing import Dict, List, Optional
from pydantic import Field
from typing_extensions import Annotated

def fetch_bus_routes(lang: str = 'en') -> List[Dict]:
    """Fetch all KMB/LWB bus routes from the API
    
    Args:
        lang: Language code (en/tc/sc) for responses
        
    Returns:
        List of route dictionaries with route details
    """
    url = "https://data.etabus.gov.hk/v1/transport/kmb/route/"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    
    # Validate language code, default to 'en' if invalid
    valid_langs = ['en', 'tc', 'sc']
    if lang not in valid_langs:
        lang = 'en'
    
    # Filter fields based on language
    filtered_routes = []
    for route in data['data']:
        filtered_routes.append({
            'route': route['route'],
            'bound': 'outbound' if route['bound'] == 'O' else 'inbound',
            'service_type': route['service_type'],
            'origin': route[f'orig_{lang}'],
            'destination': route[f'dest_{lang}']
        })
    
    return filtered_routes

def get_bus_kmb(
    lang: Annotated[Optional[str], 
          Field(description="Language (en/tc/sc) English, Traditional Chinese, Simplified Chinese. Default English",
               json_schema_extra={"enum": ["en", "tc", "sc"]})] = 'en'
) -> Dict:
    """Get all bus routes of Kowloon Motor Bus (KMB) and Long Win Bus Services Hong Kong"""
    routes = fetch_bus_routes(lang if lang else 'en')
    return {
        "type": "RouteList",
        "version": "1.0",
        "data": routes
    }
