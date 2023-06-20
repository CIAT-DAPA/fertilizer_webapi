import unittest
import requests
from agroadvisory_api import app


class TestAgroadisory(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_coordinates(self):
        """  for this endoint we need to build an url to do a request, that url needs a library called  URLSearchParams, this join a parametres and create an url
            example of parametres:
            parameters={
                    'service':'WMS',
                    'version':'1.1.1',
                    'request':'GetFeatureInfo',
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
            layer is a input in he API, example: et_wheat_compost_probabilistic_below
            the url is built like this: URL=str(URLSearchParams(GEOSERVER_URL + SERVICEE).append(parameters))
            GEOSERVER_URL value never change and the value is : "https://geo.aclimate.org/geoserver/fertilizer_et/"
            SERVICEE value never change and the value is "wms" 
            in parameters lat and lon are taken from an array od coodinates that we sent like parmeters.
            in api_module/coordinates.py is the full code 
             examples of url: "https://geo.aclimate.org/geoserver/fertilizer_et/wms?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=et_wheat_compost_probabilistic_below&query_layers=et_wheat_compost_probabilistic_below&feature_count=10&info_format=application%2Fjson&format_options=callback%3AhandleJson&SrsName=EPSG%3A4326&width=101&height=101&x=50&y=50&bbox=36.41521%2C8.25343%2C36.615210000000005%2C8.453429999999999",

             "https://geo.aclimate.org/geoserver/fertilizer_et/wms?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=et_wheat_compost_probabilistic_above&query_layers=et_wheat_compost_probabilistic_above&feature_count=10&info_format=application%2Fjson&format_options=callback%3AhandleJson&SrsName=EPSG%3A4326&width=101&height=101&x=50&y=50&bbox=36.47521%2C8.25343%2C36.67521%2C8.453429999999999"
             """
        
        response = requests.get('https://geo.aclimate.org/geoserver/fertilizer_et/wms?service=WMS&version=1.1.1&request=GetFeatureInfo&time=2022-07&layers=et_wheat_compost_probabilistic_below&query_layers=et_wheat_compost_probabilistic_below&feature_count=10&info_format=application%2Fjson&format_options=callback%3AhandleJson&SrsName=EPSG%3A4326&width=101&height=101&x=50&y=50&bbox=36.41521%2C8.25343%2C36.615210000000005%2C8.453429999999999',headers={"Content-Type": "application/json"})
        responseNotFund = requests.get('https://geo.aclimate.org/geoserver/fertilizer_et/oms?service=WMS&version=1.1.1&request=GetFeatureInfo&layers=et_wheat_compost_probabilistic_above&query_layers=et_wheat_compost_probabilistic_above&feature_count=10&info_format=application%2Fjson&format_options=callback%3AhandleJson&SrsName=EPSG%3A4326&width=101&height=101&x=50&y=50&bbox=36.47521%2C8.25343%2C36.67521%2C8.453429999999999',headers={"Content-Type": "application/json"})
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(404, responseNotFund.status_code)
        self.assertEqual(response.json()['features'][0]['properties']['GRAY_INDEX']!=0,True)


if __name__ == "__main__":
    unittest.main()