import unittest
import requests
from agroadvisory_api import app
from mongoengine import connect, disconnect


class TestAgroadisory(unittest.TestCase):

    def setUp(self):
        connect('mongoenginetest', host='mongomock://localhost')
        self.app = app.test_client()

    def test_single_adm3(self):
        #this endpoint receives one paremeter after adm3/ (woreda) that correspond to the admistrative level 2
        #examples: 637e453d6b22dee825f5b37c,637e453d6b22dee825f5b37d,637e453d6b22dee825f5b37e
        response = self.app.get('http://127.0.0.1:5000/adm3/637e453d6b22dee825f5b37e',headers={"Content-Type": "application/json"}) #status code 200
        #responseNullArray = self.app.get('http://127.0.0.1:5000/adm3/637e453d6b22dee825f5b17c',headers={"Content-Type": "application/json"}) #status code 200
        #responseValidationError = self.app.get('http://127.0.0.1:5000/adm3/637e453d6b22dee825f5b37i',headers={"Content-Type": "application/json"}) #status code 200
        responseNotFound = self.app.get('http://127.0.0.1:5000/adm3/637e453d6b22dee825f5b37e/',headers={"Content-Type": "application/json"}) #status code 404
        self.assertEqual(200, response.status_code)
        self.assertEqual(404, responseNotFound.status_code)
        #self.assertEqual(500, responseValidationError.status_code)
        #self.assertEqual(len(response.json())>0,True)
        #self.assertEqual(len(responseNullArray.json()),0)


if __name__ == "__main__":
    unittest.main()