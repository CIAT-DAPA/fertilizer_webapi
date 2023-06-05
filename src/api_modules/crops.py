from flask import Flask, jsonify
from flask_restful import Resource
from orm.database import Crop
import json

class Crops(Resource):

    def __init__(self):
        super().__init__()

    def get(self):
        """
        Get all crops from database
        ---
        description: Query all the crops, this endpoint has not parameters and will respond with the list of all crops
        responses:
          200:
            description: Crop
            schema:
              id: Crop
              properties:
                id:
                  type: string
                  description: Crop ID
                name:
                  type: string
                  description: Crop name
        """
        q_set = None
        q_set = Crop.objects()
        json_data = [{"id":str(x.id),"name":x.name} for x in q_set]
        return json_data
