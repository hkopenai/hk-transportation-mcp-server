import unittest
from tests.test_tool_passenger_traffic import TestPassengerTraffic
from tests.test_tool_bus_kmb import TestBusKMB

def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPassengerTraffic))
    suite.addTests(loader.loadTestsFromTestCase(TestBusKMB))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = suite()
    runner.run(test_suite)
