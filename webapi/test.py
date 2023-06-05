#import requests

#url = "https://geo.aclimate.org/geoserver/aclimate_et/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=aclimate_et:sample_kebele&maxFeatures=50&outputFormat=application%2Fjson"
#response = requests.get(url)
#print(response.content)


##############################

from mongoengine import *

# Region
class Adm1(Document):
    name = StringField(required=True)
    ext_id = StringField(required=False)

connect(host="mongodb://localhost:27017/nextgen")
print("Connected DB")
q_set = Adm1.objects()
json_data = [{"id":str(x.id),"name":x.name,"ext_id":x.ext_id} for x in q_set]
for j in json_data:
    print(j)