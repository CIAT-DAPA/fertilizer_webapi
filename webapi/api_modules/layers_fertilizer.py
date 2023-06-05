import requests
import xml.etree.ElementTree as ET

from flask_restful import Resource
from conf import config

class Layers(Resource):

    def __init__(self):
        super().__init__()

    def get(self):
        """
        Get all layers of fertilizer in the geoserver for nextgen
        ---
        description: Query all the layers. This endpoint does not receive any parameter. Returns an array with a list of the different layers on which information is available
        responses:
          200:
            description: Layers available in Geoserver
            schema:
              id: Layers
              properties:
                name:
                  type: string
                  description: Full name of layer
        """
        response = requests.get( config['GEOSERVER_URL'] + config['WORKSPACE'] + '/ows?service=wcs&version=1.1.0&request=GetCapabilities')
        
        responseXml = ET.fromstring(response.content)
        content = responseXml.find('{http://www.opengis.net/wcs/1.1.1}Contents')
        layers = {"layers":[]}
        for layer in content.findall('{http://www.opengis.net/wcs/1.1.1}CoverageSummary'):
          layers['layers'].append({"name": layer[0].text})
        return layers
