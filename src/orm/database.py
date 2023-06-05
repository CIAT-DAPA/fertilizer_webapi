from mongoengine import *

# Region
class Adm1(Document):
    name = StringField(required=True)
    ext_id = StringField(required=False)

# Zone
class Adm2(Document):
    name = StringField(required=True)
    ext_id = StringField(required=False)
    adm1 = ReferenceField(Adm1)

# Woreda
class Adm3(Document):
    name = StringField(required=True)
    ext_id = StringField(required=False)
    adm2 = ReferenceField(Adm2)

# Kebele
class Adm4(Document):
    name = StringField(required=True)
    ext_id = StringField(required=False)
    aclimate_id = StringField(required=False)
    adm3 = ReferenceField(Adm3)

class Crop(Document):
    name = StringField(required=True)

class Forecast(Document):
    date = DateTimeField(required=True)
    crop = ReferenceField(Crop)

class MetricType(Document):
    name = StringField(required=True)

class Metric(Document):
    # kebele
    adm4 = ReferenceField(Adm4)
    forecast = ReferenceField(Forecast)
    type = ReferenceField(MetricType)
    values = ListField(required= True)
    
class Risk(Document):
    # kebele
    adm4 = ReferenceField(Adm4)
    forecast = ReferenceField(Forecast)
    type = ReferenceField(MetricType)
    values = ListField(required= True)