import unittest
from tests.test_tool_business_reg import TestBusinessReturns
from tests.test_tool_passenger_traffic import TestPassengerTraffic

def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessReturns))
    suite.addTests(loader.loadTestsFromTestCase(TestPassengerTraffic))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = suite()
    runner.run(test_suite)
