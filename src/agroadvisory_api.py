
import os
import sys
from flask import Flask, redirect
from flask_restful import Api
from flask_cors import CORS
from flasgger import Swagger
from conf import config

from api_modules.kebele import Kebele
from api_modules.woreda import Woreda
#from api_modules.clipping_raster import ClippingRaster
# New Modules
from mongoengine import *
from api_modules.adm1 import AdministrativeLevel1
from api_modules.country import Countries
from api_modules.adm2 import AdministrativeLevel2
from api_modules.adm3 import AdministrativeLevel3
from api_modules.adm4 import AdministrativeLevel4
from api_modules.crops import Crops
from api_modules.forecasts import Forecasts
from api_modules.metrics import Metrics
from api_modules.metric_type import MetricType
from api_modules.risks import Risks
from api_modules.coordinates import Coordinates
from api_modules.layers_fertilizer import Layers
#from api_modules.layers import Layers


app = Flask(__name__)
CORS(app)
api = Api(app)
swagger = Swagger(app)


@app.route('/')
def home():
    return redirect("/apidocs")


#api.add_resource(Woreda, '/woredas', endpoint="woredas")
#api.add_resource(Woreda, '/woredas/<woreda_name>', endpoint="woreda")
#api.add_resource(Kebele, '/kebele/<kebele_name>')
#api.add_resource(ClippingRaster, '/clip_raster')

# New methods
api.add_resource(AdministrativeLevel1, '/adm1/<country>')
api.add_resource(Countries, '/country')
api.add_resource(AdministrativeLevel2, '/adm2/<adm1>')
api.add_resource(AdministrativeLevel3, '/adm3/<adm2>')
api.add_resource(AdministrativeLevel4, '/adm4/<adm3>')
api.add_resource(Crops, '/crops')
api.add_resource(Forecasts, '/forecast/<crop>')
api.add_resource(Metrics, '/metrics/<adm4>')
api.add_resource(Risks, '/risk/<adm4>/<forecast>')
api.add_resource(Coordinates, '/coordinates/<layer>/<coor>/<date>')
api.add_resource(Layers, '/layers_fertilizer')

#api.add_resource(Layers, '/layers')
#api.add_resource(MetricType, '/metric_types')




if __name__ == '__main__':
    connect(host=config['CONNECTION_DB'])
    print("Connected DB")
    
    if config['DEBUG']:
        app.run(threaded=True, port=config['PORT'], debug=config['DEBUG'])
    else:
        app.run(host=config['HOST'], port=config['PORT'],
                debug=config['DEBUG'])

# nohup python3 agroadvisory_api.py > log.txt 2>&1 &
