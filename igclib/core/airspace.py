from igclib.geography.converters import parse_altitude
from shapely import Point, Polygon

class Airspace:

    def __init__(self, record):
        self.name = record.get('name')
        self.floor = parse_altitude(record.get('floor'))
        self.ceiling = parse_altitude(record.get('ceiling'))
        self.elements = record.get('elements')
        self.airspace_class = record.get('class')
        self.box = self.get_bounding_box()

    def get_bounding_box(self):
        pass
        

    def __contains__(self, point):
        if point.altitude > self.ceiling or point.altitude < self.floor:
            return False
        
        return True
