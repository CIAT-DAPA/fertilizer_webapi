import unittest
import requests
from agroadvisory_api import app
from unit_tests.mongo_test_setup import use_mongomock, teardown_mongomock


class TestAgroadisory(unittest.TestCase):

    def setUp(self):
        use_mongomock()
        self.app = app.test_client()

    def tearDown(self):
        teardown_mongomock()

    def test_crops(self):
        #this endpoint has no parameteres (crop)
        response = self.app.get('http://127.0.0.1:5000/crops',headers={"Content-Type": "application/json"})
        responseNotFound = self.app.get('http://127.0.0.1:5000/crops/',headers={"Content-Type": "application/json"})
        print(response)
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(404, responseNotFound.status_code)


if __name__ == "__main__":
    unittest.main()