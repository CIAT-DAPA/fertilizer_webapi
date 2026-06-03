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

    def test_single_adm4(self):
        #this endpoint receives one paremeter after adm4/(Kebele) that correspond to the admistrative level 3
        #examples: 637e45476b22dee825f5b4a6, 637e45476b22dee825f5b4a7, 637e45476b22dee825f5b4a9
        response = self.app.get('http://127.0.0.1:5000/adm4/637e45476b22dee825f5b4a7',headers={"Content-Type": "application/json"})
        #responseValidationError = self.app.get('http://127.0.0.1:5000/adm4/637e45476b22dee825f5b4ai',headers={"Content-Type": "application/json"})
        #responseNullArray = self.app.get('http://127.0.0.1:5000/adm4/637e45476b22dee825f5c4a2',headers={"Content-Type": "application/json"})
        #responseWithContent = self.app.get('http://127.0.0.1:5000/adm4/637e45476b22dee825f5b4a9',headers={"Content-Type": "application/json"})
        responseNotFound = self.app.get('http://127.0.0.1:5000/adm4/637e45476b22dee825f5b4a9/',headers={"Content-Type": "application/json"})
        
        print(response)
        self.assertEqual(200, response.status_code)
        #self.assertEqual(500, responseValidationError.status_code)
        #self.assertEqual(len(responseNullArray.json()),0)
        #self.assertEqual(len(responseWithContent.json())>0,True)
        self.assertEqual(404, responseNotFound.status_code)


if __name__ == "__main__":
    unittest.main()