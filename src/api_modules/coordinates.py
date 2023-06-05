import os
from flask_restful import Resource
from URLSearchParams import URLSearchParams
import requests
import json
import ast
GEOSERVER_URL="https://geo.aclimate.org/geoserver/fertilizer_et/"
SERVICEE="wms"
#Example of layer:fertilizer_et:et_wheat_compost_probabilistic_bellow
#example of array of coordinates
class Coordinates(Resource):


    def __init__(self):
        super().__init__()
    def post(self,layer=None,coor=None,date=None):
        """
        Get Features, Information of Urea, NPS, Compost & VCompost and Optimal yield.
        ---
        description: Should be queried to obtain Urea, NPS, Compost, VCompost or Optimal Yield information for one or more coordinates. This endpoint needs two parameters, **layer** that is name of the layer (the layer names can be obtained from the endpoint `/layers_fertilizer`) and  **coor** array of objects with the coordinates you want to query lat and lon. The endpoint must follow the following format, the endpoint only allows post requests and he will respond with a list of the values of the corresponding layer for each of the coordinates.
        parameters:
          - in: path
            name: layer
            type: string
            required: true
            description: layer name at https://geo.aclimate.org/geoserver/web/wicket/bookmarkable/org.geoserver.web.demo.MapPreviewPage?8&filter=false example= et_wheat_compost_probabilistic_below
          - in: path
            name: coor
            type: array
            items:
                type: object
            required: true
            description: array of objects with coordinates lat and lon, example= [{"lat":7.17712,"lon":38.16367},{"lat":8.35343,"lon":36.51521},{"lat":8.35343,"lon":36.51521}]
          - in: path
            name: date
            type: string
            required: true
            description: date in which you want to extract the information from the mosaic, example 2022-07
        responses:
          200:
            description: Latitude, longitude and value
            schema:
              id: Features
              properties:
                lat:
                  type: number
                  format: float
                  description: lat
                  default: 8.5583
                lon:
                  type: number
                  format: float
                  description: lat
                  example: 8.5583
                value:
                  type: number
                  format: float
                  description: values
                  example: 20.00
                
        """
        arr=ast.literal_eval(coor)
        print(arr[0]['lat'])
        print(len(arr))
        list=[]
        for i in arr:
            lat=i['lat']
            lon=i['lon']
            parameters={
                'service':'WMS',
                'version':'1.1.1',
                'request':'GetFeatureInfo',
                'time':date,
                'layers':layer,
                'query_layers':layer,
                'feature_count':10,
                'info_format':'application/json',
                'format_options':'callback:handleJson',
                'SrsName':'EPSG:4326',
                'width':101,
                'height':101,
                'x':50,
                'y':50,
                'bbox':str(lon - 0.1) + ',' + str(lat - 0.1) + ',' + str(lon + 0.1) + ',' + str(lat + 0.1)}

            self.url=str(URLSearchParams(GEOSERVER_URL + SERVICEE).append(parameters))
            print(self.url)
            
            response= requests.get(self.url)
            data= response.json()
            json= data

            if 'features' in json and json['features']:
                gray_index = json['features'][0]['properties'].get('GRAY_INDEX')
                if gray_index is not None:
                    respuesta = {'layer': layer, 'lat': lat, 'lon': lon, 'value': gray_index, 'date': date}
                    if respuesta not in list:
                        list.append(respuesta)
                else:
                    respuesta = {}
            else:
                respuesta = {}

            
        return list

            
        

       
        
        
