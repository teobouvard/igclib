import json
import datetime
import numpy as np

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'to_json'):
            return obj.to_json()
        elif isinstance(obj, (datetime.time)):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return json.JSONEncoder.default(self, obj)