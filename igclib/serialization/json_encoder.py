import json
import datetime
import numpy as np

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return {x: y for x, y in obj.__dict__.items() if not x.startswith('_') and y is not None}
        elif isinstance(obj, (datetime.time)):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return json.JSONEncoder.default(self, obj)