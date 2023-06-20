import unittest
import requests
from agroadvisory_api import app
from mongoengine import connect, disconnect



class TestAgroadisory(unittest.TestCase):

    def setUp(self):
        connect('mongoenginetest', host='mongomock://localhost')
        self.app = app.test_client()

    def test_forecast(self):
        #this endpoint receives one paremeter after forecaste/ (forecast) that correspond to the crop
        #only exist one crop for now , the id is 63865d9f68c981103580abee
        response = self.app.get('http://127.0.0.1:5000/forecast/63865d9f68c981103580abee',headers={"Content-Type": "application/json"}) #status code 200
        responseNotFoud = self.app.get('http://127.0.0.1:5000/forecast/63865d9f68c981103580abee/',headers={"Content-Type": "application/json"}) #status code 404
        #responseNullArray = self.app.get('http://127.0.0.1:5000/forecast/63865d9f68c981103580abea',headers={"Content-Type": "application/json"}) #array null
        #responseVaidationError = self.app.get('http://127.0.0.1:5000/forecast/63865d9f68c981103580a',headers={"Content-Type": "application/json"}) #satus code 500
        
        print(response)
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(404, responseNotFoud.status_code)
        #self.assertEqual(500, responseVaidationError.status_code)
        #self.assertEqual(len(responseNullArray.json()),0)
        #self.assertEqual(len(response.json())>0,True)


if __name__ == "__main__":
    unittest.main()