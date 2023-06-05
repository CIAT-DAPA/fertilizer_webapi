from flask import Flask, jsonify
from flask_restful import Resource
from orm.database import Metric
import json
from bson import ObjectId

class Metrics(Resource):

    def __init__(self):
        super().__init__()

    def get(self, adm4 = None):
        """
        Get forecast data for a adminsitrative level 4 (Kebele)
        ---
        description: |- 
          Query the forecast data for administrative level 4 (Kebele). This endpoint needs one parameter, **adm4** id of the administrative levels 4 (kebele) to be queried (this id can be obtained from the endpoint `/adm4`); The API will respond with the list of the forecast data from that specific kebele.
          
          The answer is an array with different objects. Each object has a type attribute which is an id. The ids are the following: 
            •	63865d9f68c981103580abf0 - compost (tons/ha.) 
            •	63865ef468c981103580e666 - nps (kg/ha.) 
            •	638660ad68c98110358120dc - optimal yield (kg/ha.) 
            •	638662c668c9811035815b52 - urea (kg/ha.) 
            •	6386653e68c98110358195c8 - vermi compost (ton/ha.)

        parameters:
          - in: path
            name: adm4
            type: string
            required: false
        responses:
          200:
            description: Metric
            schema:
              id: Metric
              properties:
                id:
                  type: string
                  description: Metric ID
                adm4:
                  type: string
                  description: ID Administrative level 4
                forecast:
                  type: string
                  description: Forecast ID
                type:
                  type: string
                  description: Type of metric
                values:
                  type: array
                  items: {}
                  description: List of values of the metric
                 
        """
        q_set = None
        if adm4 is None:
            q_set = Metric.objects()
        else:
            ids = adm4.split(',')
            q_set = Metric.objects(adm4__in=ids)
        json_data = [{"id":str(x.id),"adm4":str(x.adm4.id),"forecast":str(x.forecast.id),"type":str(x.type.id),"values":x.values} for x in q_set]
        return json_data



