from flask import Flask, jsonify
from flask_restful import Resource
import geopandas as gpd
import pandas as pd

from conf import config


class Woreda(Resource):

    url = ""

    def __init__(self):
        self.url = config['GEOSERVER_URL'] + config['WORKSPACE'] + \
            "/ows?service="+config['SERVICE']+"&version=1.0.0&request=GetFeature&typeName=" + \
            config['LAYER_NAME'] + \
            "&maxFeatures=700&outputFormat=application%2Fjson"
        super().__init__()

    def get(self, woreda_name=None):
        """
        Get all or a specific woreda
        If you want all woredas ommit woreda_name
        Examples of woreda_name: Goba, Saya Debirna Wayu, Lenmo, Mareqo, Basona Werana

        ---
        parameters:
          - in: path
            name: woreda_name
            type: string
            required: false
        responses:
          200:
            description: A single woreda
            schema:
              id: Woreda
              properties:
                fid:
                  type: string
                  description: fid
                  default: sample_kebele.4
                Shape_Area:
                  type: integer
                  description: shape area
                  default: 0.00
                Woreda:
                  type: string
                  description: The woreda id
                  default: Woreda1
                kebele:
                  type: string
                  description: The kebele id
                  default: Kebele1
                N:
                  type: integer
                  description: Nitrogen data
                  default: 0.00
                P:
                  type: integer
                  description: Phosphorus data
                  default: 0.00
                K:
                  type: integer
                  description: Potassium data
                  default: 0.00
        """
        # Reading wfs into geodataframe
        geo_data_frame = gpd.read_file(self.url)
        # Casting to pandas dataframe (easy to manipulate)
        kebeles_data_frame = pd.DataFrame(geo_data_frame)

        # Dropping 'geometry' column
        kebeles_data_frame.drop('geometry', inplace=True, axis=1)

        if woreda_name is None:
            return kebeles_data_frame.to_json(orient='records')

        else:

            search_for = woreda_name.capitalize()

            result = kebeles_data_frame[kebeles_data_frame['W_NAME'].str.capitalize(
            )
                == search_for.capitalize()]
            if not result.empty:
                return result.to_json(orient='records')
            else:
                return 'No woreda found with id: ' + woreda_name, 404
