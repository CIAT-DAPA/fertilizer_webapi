import rasterio
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg
import pycrs

from flask import send_from_directory
from flask_restful import Resource, request
import geopandas as gpd
import pandas as pd

import shutil

import os

from conf import config

class ClippingRaster(Resource):

    url = ""

    def __init__(self):
        self.url = config['GEOSERVER_URL'] + config['WORKSPACE'] + \
            "/ows?service="+config['SERVICE']+"&version=1.0.0&request=GetFeature&typeName=" + \
            config['LAYER_NAME'] + \
            "&maxFeatures=700&outputFormat=application%2Fjson"
        super().__init__()

    def getFeatures(self, gdf):
        """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
        import json
        return [json.loads(gdf.to_json())['features'][0]['geometry']]

    def delete_folder_content(self, folder_path):
        """Function to delete al folder content"""
        list_dir = os.listdir(folder_path)
        for filename in list_dir:
            file_path = os.path.join(folder_path, filename)

            if os.path.isfile(file_path) or os.path.islink(file_path):
                print("deleting file:", file_path)
                os.unlink(file_path)

            elif os.path.isdir(file_path):
                print("deleting folder:", file_path)
                shutil.rmtree(file_path)

    def get(self):
        """
        Get a cropped raster tif file
        ---
        parameters:
          - in: path
            name: boundaries
            type: string
            required: true
            description: minx, miny, maxx, maxy separated by comas (without spaces)
          - in: path
            name: layer
            type: string
            required: true
            description: layer name at https://geo.aclimate.org/geoserver/web/wicket/bookmarkable/org.geoserver.web.data.layer.LayerPage?7&filter=true example et_wheat_compost_probabilistic_above
            
        responses:
          200:
            description: A tif file
            
        """

        self.delete_folder_content(config["FERTILIZER_RASTERS_DIR"])
        
        args = request.args
        minx, miny, maxx, maxy = args['boundaries'].split(',')
        layer = args['layer'] 

        rasters_dir = ".//raster_files//fertilizer_et//"
        
        raster_folder = rasters_dir+layer+"/"
        entries = os.listdir(raster_folder)
        
        fp = raster_folder+entries[0]
        out = config["FERTILIZER_RASTERS_DIR"]+entries[0]
        data = rasterio.open(fp)

        bbox = box(float(minx), float(miny), float(maxx), float(maxy))

        geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))
        geo = geo.to_crs(crs=data.crs.data)

        coords = self.getFeatures(geo)    

        out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)
        out_meta = data.meta.copy()
    
        epsg_code = int(data.crs.data['init'][5:])
        
        out_meta.update({"driver": "GTiff", 
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform,
                        "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()})

        with rasterio.open(out, "w", **out_meta) as dest:
            dest.write(out_img)

        print(entries[0])
        return send_from_directory(config["FERTILIZER_RASTERS_DIR"], entries[0], as_attachment=True)



