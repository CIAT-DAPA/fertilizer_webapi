
import os 

config = {}

if os.getenv('DEBUG', "true").lower() == "true":
    config['DEBUG'] = True
    config['WORKSPACE'] = "fertilizer_et"
    config['LAYER_NAME'] = config['WORKSPACE'] + \
        ":et_wheat_fertilizer_recommendation_normal"
    config['SERVICE'] = 'WFS'
    config['GEOSERVER_URL'] = "https://geo.aclimate.org/geoserver/"
    config['FERTILIZER_RASTERS_DIR'] = "./raster_files/cropped/"
    config['HOST'] = 'localhost'
    config['PORT'] = 5000
    config['CONNECTION_DB']='mongodb://root:s3cr3t@localhost:27017/nextgen?authSource=admin'
else:
    config['DEBUG'] = False
    config['WORKSPACE'] = os.getenv('WORKSPACE')
    config['LAYER_NAME'] = config['WORKSPACE']+os.getenv('LAYER_NAME')
    config['SERVICE'] = os.getenv('SERVICE')
    config['GEOSERVER_URL'] = os.getenv('GEOSERVER_URL')
    config['FERTILIZER_RASTERS_DIR'] = os.getenv('FERTILIZER_RASTERS_DIR')
    config['HOST'] = '0.0.0.0'
    config['PORT'] = os.getenv('PORT')
    config['CONNECTION_DB']=os.getenv('CONNECTION_DB')

