import unittest
from lib.auth import deviceupload

class TestLambda(unittest.TestCase):
    def setUp(self):
        self.input = {
            "data":
                {
                    "serial_number":"M2MR1020012312",
                    "battery_state": "60",
                    "time" : "2022-01-10 15:00:26.155299"
                }
            }
    def testdynamoupload(self):
        '''
        test lambda upload event
        '''     
        response = deviceupload(self.input, "")
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body']['response'], 'battery state saved')
