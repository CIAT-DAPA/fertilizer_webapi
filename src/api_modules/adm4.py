from flask import Flask, jsonify
from flask_restful import Resource
from orm.database import Adm4
import json

class AdministrativeLevel4(Resource):

    def __init__(self):
        super().__init__()

    def get(self, adm3 = None):
        """
        Get all Administrative levels 4 from database (Kebele)
        ---
        description: Query the information of the administrative levels 4 (Kebele). This endpoint needs one parameter, **adm3** that is id of the administrative levels 3 (Woreda) to be queried (this id can be obtained from the endpoint `/adm3`); The API will respond with the list of Kebeles from that specific woreda.
        parameters:
          - in: path
            name: adm3
            type: string
            required: true
        responses:
          200:
            description: Administrative levels 4
            schema:
              id: Adm4
              properties:
                id:
                  type: string
                  description: Id Administrative level 4
                name:
                  type: string
                  description: Administrative level 4 name
                ext_id:
                  type: string
                  description: Extern Id to identify Administrative level 4
                aclimate_id:
                  type: string
                  description: Id to identify Administrative level 4 in Aclimate Platform
                adm3:
                  type: string
                  description: Id Administrative level 3
        """
        q_set = None
        if adm3 is None:
            q_set = Adm4.objects()
        else:
            q_set = Adm4.objects(adm3=adm3)
        json_data = [{"id":str(x.id),"name":x.name,"ext_id":x.ext_id,"aclimate_id":x.aclimate_id,"adm3":str(x.adm3.id)} for x in q_set]
        return json_data
