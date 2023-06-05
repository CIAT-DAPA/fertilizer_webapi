from flask import Flask, request
from flask_restful import Resource, reqparse
from orm.database import Forecast
import datetime
import json

class Forecasts(Resource):

    def __init__(self):
        super().__init__()

    def get(self, crop = None):
        """
        Get forecast list from database
        ---
        description: Query the forecast list. This endpoint needs one parameter, **crop** that is id of the crop to be queried (this id can be obtained from the endpoint `/crops`). The API will respond with the list of the forecast from that specific crop.
        parameters:
          - in: path
            name: crop
            type: string
            required: true
        responses:
          200:
            description: Forecast
            schema:
              id: Forecast
              properties:
                id:
                  type: string
                  description: Id Forecast
                date:
                  type: datetime
                  description: Date of forecast
                crop:
                  type: string
                  description: Id crop
        """
        q_set = None
        if crop is None:
            q_set = Forecast.objects()
        else:
            print("entro 2")
            q_set = Forecast.objects(crop=crop)
        json_data = [{"id":str(x.id),"date":x.date.strftime("%Y-%m"),"crop":str(x.crop.id)} for x in q_set]
        return json_data
