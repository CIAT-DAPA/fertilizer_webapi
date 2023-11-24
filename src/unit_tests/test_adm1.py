import unittest
import sys
sys.path.append("./src/")
from agroadvisory_api import app
import requests
from mongoengine import connect, disconnect

import requests
class TestAgroadisory(unittest.TestCase):

    def setUp(self):
        connect('mongoenginetest', host='mongomock://localhost')
        self.app = app.test_client()

    def test_single_adm1(self):
        
        #this endpoint has no parameteres (Region)
        response =self.app.get('http://127.0.0.1:5000/adm1/6499e7df9b53ecd65bbcf67e',headers={"Content-Type": "application/json"})
        #responseNotFound =requests.get('http://127.0.0.1:5000/4555454',headers={"Content-Type": "application/json"})
        print(response)
        #print(responseNotFound)
        self.assertEqual(200, response.status_code)
        #self.assertEqual(404, responseNotFound.status_code)

 
if __name__ == "__main__":
    unittest.main()