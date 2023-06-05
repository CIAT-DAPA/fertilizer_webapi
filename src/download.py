from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
import geopandas as gpd

# WMS
#wms = WebMapService('https://geo.aclimate.org/geoserver/fertilizer_et/wms', version='1.1.1')

#print(wms.identification.type)
#print(wms.identification.version)
#[print(op.name) for op in wms.operations]

#WFS
#wfs11 = WebFeatureService(url='https://geo.aclimate.org/geoserver/fertilizer_et/wfs', version='1.1.0')
#print(wfs11.identification.title)
#[print(operation.name) for operation in wfs11.operations]


wfs_url = 'https://geo.aclimate.org/geoserver/fertilizer_et/wfs'
wfs = WebFeatureService(wfs_url, version='2.0.0')

sorted_layer_ids = list(sorted(wfs.contents.keys()))
print(sorted_layer_ids)

#canada_admin_boundaries_index = sorted_layer_ids.index('public:canada_admin_boundaries')
#for layerID in sorted_layer_ids[canada_admin_boundaries_index - 1:canada_admin_boundaries_index + 2]:

for layerID in sorted_layer_ids:
    layer = wfs[layerID]
    print('Layer ID:', layerID)
    print('Title:', layer.title)
    print('Boundaries:', layer.boundingBoxWGS84, '\n')


layer_id = sorted_layer_ids[0]
meta = wfs.contents[layer_id]
print(meta.title)

# Get the actual data
data = wfs.getfeature(typename=layer_id, bbox=(37.7, 6.7, 40, 10), outputFormat='JSON')

# Write to file
fn = 'output.geojson'
with open(fn, 'wb') as fh:
    fh.write(data.read())

layers = gpd.read_file(fn)
layers.plot()
