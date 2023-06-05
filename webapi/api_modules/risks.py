from flask import Flask, jsonify
from flask_restful import Resource
from orm.database import Risk
import json

class Risks(Resource):

    def __init__(self):
        super().__init__()

    def get(self, adm4 = None):
        """
        Get Risk data for a adminsitrative level 4 (Kebele)
        ---
        description: Query the risk data for administrative level 4 (Kebele). This endpoint needs one parameter, **adm4** id of the administrative levels 4 (kebele) to be queried (this id can be obtained from the endpoint `/adm4`; The API will respond a object with the list of the risk data from that specific kebele.
        parameters:
          - in: path
            name: adm4
            type: string
            required: false
        responses:
          200:
            description: Risk
            schema:
              id: Risk
              properties:
                id:
                  type: string
                  description: Id Risk
                adm4:
                  type: string
                  description: ID Administrative level 4
                forecast:
                  type: string
                  description: Forecast ID
                type:
                  type: string
                  description: Type of metric
                risk:
                  description: list risk
                  type: object
                  properties: 
                    name: 
                      type: string
                    values:
                      type: array
                      items: {}
                      description: Value of risk
                  
        """
        q_set = None
        if adm4 is None:
            q_set = Risk.objects()
        else:
            ids = adm4.split(',')
            q_set = Risk.objects(adm4__in=ids)
        json_data = [{"id":str(x.id),"adm4":str(x.adm4.id),"forecast":str(x.forecast.id),"type":str(x.type.id),"risk":x.values[0]} for x in q_set]
        return json_data
        