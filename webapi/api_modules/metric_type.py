from flask import Flask, request
from flask_restful import Resource, reqparse
from orm.database import MetricType
import datetime
import json

class MetricType(Resource):

    def __init__(self):
        super().__init__()

    def get(self):
        """
        Get metric type list from database
        ---
        parameters:
          - in: path
            name: type
            type: string
            required: false
        responses:
          200:
            description: Metric type
            schema:
              id: Metric type
              properties:
                id:
                  type: string
                  description: Id metric type
                name:
                  type: string
                  description: name of the metric
              
        """
        q_set = None
        q_set = MetricType.objects()
        json_data = [{"id":str(x.id),"name":x.name} for x in q_set]
        return json_data
