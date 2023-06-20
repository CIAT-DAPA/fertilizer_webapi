import unittest
import requests
from agroadvisory_api import app
from mongoengine import connect, disconnect


class TestAgroadisory(unittest.TestCase):

    def setUp(self):
        connect('mongoenginetest', host='mongomock://localhost')
        self.app = app.test_client()

    def test_single_risk(self):
        #this endpoint receives one paremeter after risk/(risk)) that correspond to the admistrative level 4 (Kebele)
        #examples: 63850dba9d578e523c7eabfd, 63850dba9d578e523c7eac02, 63850dfd9d578e523c7ec346
        response = self.app.get('http://127.0.0.1:5000/risk/63850dba9d578e523c7eac02',headers={"Content-Type": "application/json"}) #statuscode 200
        #responseValidationError = self.app.get('http://127.0.0.1:5000/risk/63850d9a9d578e523c7e9bcb8',headers={"Content-Type": "application/json"}) #statusCode 500
        #responseNullArray = self.app.get('http://127.0.0.1:5000/risk/63850dfd9d578e523c7ec312',headers={"Content-Type": "application/json"}) #response a null array
        responseNotFound = self.app.get('http://127.0.0.1:5000/riskk/63850dfd9d578e523c7ec312',headers={"Content-Type": "application/json"}) #response a null array
        
        #print(len(responseNullArray.json()))
        #print(response)
        self.assertEqual(200, response.status_code)
        #self.assertEqual(500, responseValidationError.status_code)
        #self.assertEqual(len(responseNullArray.json()), 0)
       # self.assertEqual(len(response.json())>0, True)
        self.assertEqual(404,responseNotFound.status_code)


if __name__ == "__main__":
    unittest.main()