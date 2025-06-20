import unittest
from unittest.mock import patch, mock_open
import json
from hkopenai.hk_transportation_mcp_server.tool_bus_kmb import fetch_bus_routes

class TestBusKMB(unittest.TestCase):
    API_RESPONSE = {
        "type": "RouteList",
        "version": "1.0",
        "generated_timestamp": "2025-06-12T21:32:34+08:00",
        "data": [
            {
                "route": "1",
                "bound": "O",
                "service_type": "1",
                "orig_en": "CHUK YUEN ESTATE",
                "orig_tc": "竹園邨",
                "orig_sc": "竹园邨",
                "dest_en": "STAR FERRY",
                "dest_tc": "尖沙咀碼頭",
                "dest_sc": "尖沙咀码头"
            },
            {
                "route": "1",
                "bound": "I",
                "service_type": "1",
                "orig_en": "STAR FERRY",
                "orig_tc": "尖沙咀碼頭",
                "orig_sc": "尖沙咀码头",
                "dest_en": "CHUK YUEN ESTATE",
                "dest_tc": "竹園邨",
                "dest_sc": "竹园邨"
            }
        ]
    }

    def setUp(self):
        self.mock_urlopen = patch('urllib.request.urlopen').start()
        self.mock_urlopen.return_value = mock_open(
            read_data=json.dumps(self.API_RESPONSE).encode('utf-8')
        )()
        self.addCleanup(patch.stopall)

    def test_fetch_bus_routes_default_lang(self):
        result = fetch_bus_routes()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['route'], '1')
        self.assertEqual(result[0]['bound'], 'outbound')
        self.assertEqual(result[0]['origin'], 'CHUK YUEN ESTATE')
        self.assertEqual(result[0]['destination'], 'STAR FERRY')
        self.assertEqual(result[1]['bound'], 'inbound')

    def test_fetch_bus_routes_tc_lang(self):
        result = fetch_bus_routes('tc')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['origin'], '竹園邨')
        self.assertEqual(result[0]['destination'], '尖沙咀碼頭')

    def test_fetch_bus_routes_sc_lang(self):
        result = fetch_bus_routes('sc')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['origin'], '竹园邨')
        self.assertEqual(result[0]['destination'], '尖沙咀码头')

    def test_invalid_language_code(self):
        result = fetch_bus_routes('xx')  # Invalid language code
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['origin'], 'CHUK YUEN ESTATE')  # Should default to English

    def test_api_unavailable(self):
        with patch('urllib.request.urlopen', side_effect=Exception('Connection error')):
            with self.assertRaises(Exception):
                fetch_bus_routes()

    def test_invalid_json_response(self):
        with patch('urllib.request.urlopen', return_value=mock_open(read_data=b'Invalid JSON')()):
            with self.assertRaises(json.JSONDecodeError):
                fetch_bus_routes()

    def test_empty_data_response(self):
        empty_response = {
            "type": "RouteList",
            "version": "1.0",
            "generated_timestamp": "2025-06-12T21:32:34+08:00",
            "data": []
        }
        with patch('urllib.request.urlopen', return_value=mock_open(read_data=json.dumps(empty_response).encode('utf-8'))()):
            result = fetch_bus_routes()
            self.assertEqual(len(result), 0)

if __name__ == "__main__":
    unittest.main()
