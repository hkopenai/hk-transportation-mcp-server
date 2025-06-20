import unittest
from unittest.mock import patch, mock_open
from hkopenai.hk_transportation_mcp_server.tool_passenger_traffic import fetch_passenger_traffic_data
from datetime import datetime, timedelta

class TestPassengerTraffic(unittest.TestCase):
    CSV_DATA = """\ufeffDate,Control Point,Arrival / Departure,Hong Kong Residents,Mainland Visitors,Other Visitors,Total
01-01-2021,Airport,Arrival,341,0,9,350
01-01-2021,Airport,Departure,803,17,28,848
02-01-2021,Airport,Arrival,363,10,10,383
02-01-2021,Airport,Departure,940,22,33,995
03-01-2021,Airport,Arrival,880,4,36,920
03-01-2021,Airport,Departure,1146,31,44,1221
04-01-2021,Airport,Arrival,445,1,12,458
04-01-2021,Airport,Departure,455,2,41,498
05-01-2021,Airport,Arrival,500,5,15,520
05-01-2021,Airport,Departure,600,25,35,660
06-01-2021,Airport,Arrival,550,8,18,576
06-01-2021,Airport,Departure,700,30,40,770
07-01-2021,Airport,Arrival,600,10,20,630
07-01-2021,Airport,Departure,800,35,45,880
08-01-2021,Airport,Arrival,650,12,22,684
08-01-2021,Airport,Departure,850,40,50,940
"""

    def setUp(self):
        self.mock_urlopen = patch('urllib.request.urlopen').start()
        self.mock_urlopen.return_value = mock_open(read_data=self.CSV_DATA.encode('utf-8'))()
        
        # Mock get_current_date() to return fixed date matching test data
        self.mock_date = patch('hkopenai.hk_transportation_mcp_server.tool_passenger_traffic.get_current_date').start()
        self.mock_date.return_value = datetime(2021, 1, 8)  # Matches latest date in test data
        
        self.addCleanup(patch.stopall)

    @patch('urllib.request.urlopen')
    def test_fetch_passenger_traffic_data(self, mock_urlopen):
        mock_urlopen.return_value = mock_open(read_data=self.CSV_DATA.encode('utf-8'))()
        
        result = fetch_passenger_traffic_data()
        
        # Should return last 7 days by default
        self.assertEqual(len(result), 14)  # 7 days * 2 directions
        self.assertEqual(result[0], {
            'date': '08-01-2021',
            'control_point': 'Airport',
            'direction': 'Arrival',
            'hk_residents': 650,
            'mainland_visitors': 12,
            'other_visitors': 22,
            'total': 684
        })

    def test_start_date_filter(self):
        with patch('urllib.request.urlopen', return_value=mock_open(read_data=self.CSV_DATA.encode('utf-8'))()):
            result = fetch_passenger_traffic_data(start_date='03-01-2021')
            self.assertEqual(len(result), 12)  # 6 days * 2 directions
            self.assertEqual(result[0]['date'], '08-01-2021')

    def test_end_date_filter(self):
        with patch('urllib.request.urlopen', return_value=mock_open(read_data=self.CSV_DATA.encode('utf-8'))()):
            result = fetch_passenger_traffic_data(end_date='03-01-2021')
            self.assertEqual(len(result), 6)  # 3 days * 2 directions
            self.assertEqual(result[-1]['date'], '01-01-2021')

    def test_both_date_filters(self):
        with patch('urllib.request.urlopen', return_value=mock_open(read_data=self.CSV_DATA.encode('utf-8'))()):
            result = fetch_passenger_traffic_data(
                start_date='02-01-2021',
                end_date='04-01-2021',
            )
            self.assertEqual(len(result), 6)  # 3 days * 2 directions
            self.assertEqual(result[0]['date'], '04-01-2021')
            self.assertEqual(result[-1]['date'], '02-01-2021')

    def test_invalid_date_format(self):
        with patch('urllib.request.urlopen', return_value=mock_open(read_data=self.CSV_DATA.encode('utf-8'))()):
            with self.assertRaises(ValueError):
                fetch_passenger_traffic_data(start_date='2021-01-02')  # Wrong format
            with self.assertRaises(ValueError):
                fetch_passenger_traffic_data(end_date='2021-01-02')  # Wrong format

    def test_dates_out_of_range(self):
        with patch('urllib.request.urlopen', return_value=mock_open(read_data=self.CSV_DATA.encode('utf-8'))()):
            result = fetch_passenger_traffic_data(start_date='01-01-2020')  # Before data range
            self.assertEqual(len(result), 16)  # Should return all data
            result = fetch_passenger_traffic_data(end_date='01-01-2022')  # After data range
            self.assertEqual(len(result), 0)  # No data can be return

    def test_data_source_unavailable(self):
        with patch('urllib.request.urlopen', side_effect=Exception('Connection error')):
            with self.assertRaises(Exception):
                fetch_passenger_traffic_data()

    def test_malformed_csv_data(self):
        malformed_data = """\ufeffDate,Control Point,Arrival / Departure,Hong Kong Residents,Mainland Visitors,Other Visitors,Total
01-01-2021,Airport,Arrival,invalid,0,9,350
"""
        with patch('urllib.request.urlopen', return_value=mock_open(read_data=malformed_data.encode('utf-8'))()):
            with self.assertRaises(ValueError):
                fetch_passenger_traffic_data()

if __name__ == '__main__':
    unittest.main()
