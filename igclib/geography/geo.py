from igclib.constants import TOLERANCE
from igclib.geography import distance


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
        return abs(distance(self, wpt) - wpt.radius) < 10 + wpt.radius * TOLERANCE

    def __getitem__(self, x):
        if x == 0:
            return self.lat
        elif x == 1:
            return self.lon
        elif x == 2:
            return self.altitude
        else:
            raise KeyError(f'x must be 0 (lat), 1 (lon) or 2 (alt) but was {x}')


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

    def __contains__(self, point):
        return True if distance(self, point) < self.radius else False


class Opti():
    """
    Opti
    """

    def __init__(self, dist, legs, points, angles):
        self.distance = dist
        self.legs = legs
        self.points = points
        self._angles = angles
