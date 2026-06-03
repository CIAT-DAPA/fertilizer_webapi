from flask_restful import Resource
from bson import ObjectId, DBRef
from bson.errors import InvalidId
from mongoengine.connection import get_db


def _parse_adm4_ids(adm4_param):
    if not adm4_param:
        return None
    oids = []
    for part in adm4_param.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            oids.append(ObjectId(part))
        except InvalidId:
            continue
    return oids or None


def _load_metric_types(db, type_ids):
    """Map metric_type ObjectId -> name without MongoEngine document dereference."""
    if not type_ids:
        return {}
    names = {}
    for doc in db.metric_type.find({"_id": {"$in": list(type_ids)}}, {"name": 1}):
        names[doc["_id"]] = doc.get("name")
    return names


def _field_id_str(value):
    """Serialize ObjectId, DBRef, or string ids without MongoEngine dereference."""
    if value is None:
        return None
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, DBRef):
        return str(value.id)
    return str(value)


def _serialize_metric_docs(raw_docs, type_names):
    rows = []
    for doc in raw_docs:
        try:
            tid = doc.get("type")
            rows.append(
                {
                    "id": str(doc["_id"]),
                    "adm4": _field_id_str(doc.get("adm4")),
                    "forecast": _field_id_str(doc.get("forecast")),
                    "type": _field_id_str(tid),
                    "type_name": type_names.get(tid) if tid is not None else None,
                    "values": doc.get("values") or [],
                }
            )
        except Exception:
            continue
    return rows


class Metrics(Resource):

    def __init__(self):
        super().__init__()

    def get(self, adm4=None):
        """
        Get forecast data for a adminsitrative level 4 (Kebele)
        ---
        description: |-
          Query the forecast data for administrative level 4 (Kebele). This endpoint needs one parameter, **adm4** id of the administrative levels 4 (kebele) to be queried (this id can be obtained from the endpoint `/adm4`); The API will respond with the list of the forecast data from that specific kebele.

          The answer is an array with different objects. Each object has a type attribute which is an id. The ids are the following:
            •	63865d9f68c981103580abf0 - compost (tons/ha.)
            •	63865ef468c981103580e666 - nps (kg/ha.)
            •	638660ad68c98110358120dc - optimal yield (kg/ha.)
            •	638662c668c9811035815b52 - urea (kg/ha.)
            •	6386653e68c98110358195c8 - vermi compost (ton/ha.)

        parameters:
          - in: path
            name: adm4
            type: string
            required: false
        responses:
          200:
            description: Metric
            schema:
              id: Metric
              properties:
                id:
                  type: string
                  description: Metric ID
                adm4:
                  type: string
                  description: ID Administrative level 4
                forecast:
                  type: string
                  description: Forecast ID
                type:
                  type: string
                  description: Type of metric
                values:
                  type: array
                  items: {}
                  description: List of values of the metric

        """
        try:
            db = get_db()
            coll = db.metric
            adm4_ids = _parse_adm4_ids(adm4)

            if adm4_ids is None:
                raw_docs = list(coll.find({}))
            else:
                # Match ObjectId or legacy string adm4 keys in metric collection.
                adm4_keys = adm4_ids + [str(oid) for oid in adm4_ids]
                raw_docs = list(coll.find({"adm4": {"$in": adm4_keys}}))

            type_ids = {doc.get("type") for doc in raw_docs if doc.get("type")}
            type_names = _load_metric_types(db, type_ids)
            return _serialize_metric_docs(raw_docs, type_names)
        except Exception as exc:
            import traceback

            traceback.print_exc()
            # Return empty list (not HTML 500) so the dashboard can show a clear empty state.
            return []
