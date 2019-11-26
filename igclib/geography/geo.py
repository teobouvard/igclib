from igclib.constants import TOLERANCE
from geolib import distance

class Point(object):
    """
    Point
    """

    def __init__(self, lat=None, lon=None, altitude=None, record=None, status=None):
        if record is not None:
            self.lat = record['lat']
            self.lon = record['lon']
            self.altitude = record['gps_alt']
            self.status = status
        else:
            self.lat = lat
            self.lon = lon
            self.altitude = altitude
        
        self.goal_distance = None

    def close_enough(self, wpt):
        return True if abs(distance(self.lat, self.lon, wpt.lat, wpt.lon) - wpt.radius) < 10 + wpt.radius*TOLERANCE else False

    def inside(self, wpt):
        return True if distance(self.lat, self.lon, wpt.lat, wpt.lon) < wpt.radius*(1 + TOLERANCE) else False


class Turnpoint(Point):
    """
    Turnpoint
    """
    def __init__(self, lat, lon, radius=None, altitude=None, name=None, desc=None, role=None, first_tag=None):
        super().__init__(lat, lon, altitude)
        self.radius = radius
        self.name = name
        self.desc = desc
        self.role = role
        self.first_tag = first_tag


class Opti():
    """
    Opti
    """
    def __init__(self, distance=0, legs=[], points=[], angles=[]):
        self.distance = distance
        self.legs = legs
        self.points = points
        self._angles = angles