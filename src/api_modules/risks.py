from flask import Flask, jsonify
from flask_restful import Resource
from bson import ObjectId
from bson.errors import InvalidId

from orm.database import Risk, MetricType


class Risks(Resource):

    def __init__(self):
        super().__init__()

    def get(self, adm4=None, forecast=None):
        """
        Get Risk data for a adminsitrative level 4 (Kebele)
        ---
        description: Query the risk data for administrative level 4 (Kebele). This endpoint needs two parameter, **adm4** id of the administrative levels 4 (kebele) to be queried (this id can be obtained from the endpoint `/adm4`, and a second parameter **forecast** this id can be obtained from the endpoint `/forecast`  The API will respond a object with the list of the risk data from that specific kebele.
        parameters:
          - in: path
            name: adm4
            type: string
            required: false
          - in: path
            name: forecast
            type: string
            required: false
        responses:
          200:
            description: Risk
            schema:
              id: Risk
              properties:
                id:
                  type: string
                  description: Id Risk
                adm4:
                  type: string
                  description: ID Administrative level 4
                forecast:
                  type: string
                  description: Forecast ID
                type:
                  type: string
                  description: Type of metric
                risk:
                  description: list risk
                  type: object
                  properties:
                    name:
                      type: string
                    values:
                      type: array
                      items: {}
                      description: Value of risk

        """
        if adm4 is None:
            qs = Risk.objects()
        else:
            oids = []
            for part in adm4.split(","):
                part = part.strip()
                if not part:
                    continue
                try:
                    oids.append(ObjectId(part))
                except InvalidId:
                    continue
            if not oids:
                return []
            qs = Risk.objects(adm4__in=oids)
        if forecast is not None:
            try:
                qs = qs.filter(forecast=ObjectId(forecast))
            except InvalidId:
                return []

        raw_docs = list(qs.as_pymongo())
        type_ids = {doc.get("type") for doc in raw_docs if doc.get("type")}
        type_names = {}
        if type_ids:
            for mt in MetricType.objects(id__in=list(type_ids)):
                type_names[mt.id] = mt.name

        json_data = []
        for doc in raw_docs:
            tid = doc.get("type")
            values = doc.get("values") or []
            json_data.append(
                {
                    "id": str(doc["_id"]),
                    "adm4": str(doc["adm4"]) if doc.get("adm4") is not None else None,
                    "forecast": str(doc["forecast"]) if doc.get("forecast") is not None else None,
                    "type": str(tid) if tid is not None else None,
                    "type_name": type_names.get(tid) if tid is not None else None,
                    "risk": values[0] if values else None,
                }
            )
        return json_data
