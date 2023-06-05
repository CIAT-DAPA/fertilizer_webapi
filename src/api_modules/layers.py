from flask import Flask, jsonify

from flask_restful import Resource
import requests
import json

class Layers(Resource):

    def __init__(self):
        super().__init__()

    def get(self):
        """
        Get all layers in the geoserver for nextgen
        ---
        responses:
          200:
            description: Layers available in Geoserver
            schema:
              id: Layer
              properties:
                name:
                  type: string
                  description: Full name of layer
        """
        q_set = None
        response = requests.get('https://geo.aclimate.org/geoserver/rest/layers.json',auth = HTTPBasicAuth('geoserver', 'SCG0vw>l2cF7vG'))
        print(response.json())
        return response.json()
