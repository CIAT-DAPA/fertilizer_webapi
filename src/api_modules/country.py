from flask import Flask, jsonify
from flask_restful import Resource
from orm.database import Country
import json

class Countries(Resource):

    def __init__(self):
        super().__init__()

    def get(self):
        """
        Get all conuntries in the database
        ---
        description: Query the information of all countries and the API will respond with the list of all countries, this endpoint has no parameters.
        responses:
          200:
            description: Countries
            schema:
              id: country
              properties:
                id:
                  type: string
                  description: Id Country
                name:
                  type: string
                  description: Country name
        """
        q_set = None
        q_set = Country.objects()
        print(q_set)
        json_data = [{"id":str(x.id),"name":x.name,"iso2":x.iso2} for x in q_set]
        return json_data



