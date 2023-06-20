import unittest
import requests
import sys
sys.path.append("./src/")
from agroadvisory_api import app
from mongoengine import connect, disconnect

class TestAgroadisory(unittest.TestCase):

    def setUp(self):
        connect('mongoenginetest', host='mongomock://localhost')
        self.app = app.test_client()

    def test_single_adm2(self):
        #this endpoint receives one paremeter after adm2/ (Zone) that correspond to the admistrative level 1
        #examples: 637e450d6b22dee825f5b35b, 637e450d6b22dee825f5b35c,637e450d6b22dee825f5b35d
        response = self.app.get('http://127.0.0.1:5000/adm2/637e450d6b22dee825f5b35b',headers={"Content-Type": "application/json"}) #status code 200
        #responseNullArray = requests.get('http://127.0.0.1:5000/adm2/637e450d6b22dee825f5b359',headers={"Content-Type": "application/json"}) #return an null array
        #responseWithContent = requests.get('http://127.0.0.1:5000/adm2/637e450d6b22dee825f5b35b',headers={"Content-Type": "application/json"})
        #responseValidationError = self.app.get('http://127.0.0.1:5000/adm2/637e453d6b22dee825f5b37i',headers={"Content-Type": "application/json"}) #status code 200
         #return an array with content
        responseNotFound = self.app.get('http://127.0.0.1:5000/adm2/637e450d6b22dee825f5b359/',headers={"Content-Type": "application/json"}) #status code 404
        self.assertEqual(200, response.status_code)
        #self.assertEqual(500, responseValidationError.status_code)
        #self.assertEqual(len(responseNullArray.json()),0)
        #self.assertEqual(len(responseWithContent.json())>0,True)
        self.assertEqual(404, responseNotFound.status_code)



if __name__ == "__main__":
    unittest.main()