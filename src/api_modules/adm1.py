from flask import Flask, jsonify
from flask_restful import Resource
from orm.database import Adm1
import json

class AdministrativeLevel1(Resource):

    def __init__(self):
        super().__init__()

    def get(self, country=None):
        """
        Get all Administrative levels 1 from database (Regions)
        ---
        description: Query the information of all administrative levels 1 and the API will respond with the list of all regions, This endpoint needs one parameter, **counrty** that is id of the countries to be queried (this id can be obtained from the endpoint `/country`); The API will respond with the list of the region from that specific country.
        parameters:
          - in: path
            name: country
            type: string
            required: true
        responses:
          200:
            description: Administrative level 1
            schema:
              id: Adm1
              properties:
                id:
                  type: string
                  description: Id Administrative level 1
                name:
                  type: string
                  description: Administrative level 1 name
                ext_id:
                  type: string
                  description: Extern Id to identify Administrative level 1
                country:
                  type: string
                  description: Id of the country
        """
        q_set = None
        if country is None:
            q_set = Adm1.objects()
        else:
            q_set = Adm1.objects(country=country)
        json_data = [{"id":str(x.id),"name":x.name,"ext_id":x.ext_id,"country":str(x.country.id)} for x in q_set]
        return json_data



