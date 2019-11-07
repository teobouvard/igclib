from igclib.constants import TOLERANCE
from igclib.constants import distance_computation as distance

class Point():
    """
    Point
    """

    def __init__(self, lat=None, lon=None, altitude=None, record=None):
        if record is not None:
            self.lat = record['lat']
            self.lon = record['lon']
            self.altitude = record['gps_alt']
        else:
            self.lat = lat
            self.lon = lon
            self.altitude = altitude
        
        self.goal_distance = None

    def close_enough(self, wpt):
        return True if abs(distance(self.lat, self.lon, wpt.lat, wpt.lon) - wpt.radius) < wpt.radius*TOLERANCE else False
    
    def to_json(self):
        return self.__dict__


class Turnpoint(Point):
    """
    Turnpoint
    """

    def __init__(self, lat, lon, radius=None, altitude=None, name=None, desc=None, role=None, direction=None):
        super().__init__(lat, lon, altitude)
        self.radius = radius
        self.name = name
        self.desc = desc
        self.role = role
        self.direction = direction
    
    def to_json(self):
        return self.__dict__


class Opti():
    """
    Opti
    """

    def __init__(self, distance=0, legs=[], points=[], angles=[]):
        self.distance = distance
        self.legs = legs
        self.points = points
        self.angles = angles

    def to_json(self):
        obj = dict(points=self.points, distance=self.distance, legs=self.legs)
        return obj