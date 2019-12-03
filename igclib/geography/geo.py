from igclib.constants import TOLERANCE
from igclib.geography import distance, heading
from shapely import geometry


class GeoPoint:
    """
    GeoPoint
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
        # TODO delete when proper task validation
        return abs(distance(self, wpt) - wpt.radius) < 10 + wpt.radius * TOLERANCE

    def __getitem__(self, key):
        if key == 0:
            return self.lat
        elif key == 1:
            return self.lon
        else:
            raise IndexError


class Turnpoint(GeoPoint):
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
        return distance(self, point) < self.radius

class Arc:
    """
    Arc
    """

    def __init__(self, lat, lon, p1=None, p2=None, radius=None):
        self.lat = lat
        self.lon = lon
        if radius is not None:
            self.radius = radius
            self.start_angle = -180
            self.end_angle = 180
        else:
            # why these two distances are not necessary equal is a mystery
            self.radius = max(distance(self, p1), distance(self, p2))
            p1_heading = heading(self, p1)
            p2_heading = heading(self, p2)
            self.start_angle = min(p1_heading, p2_heading)
            self.end_angle = max(p1_heading, p2_heading)

    def __contains__(self, point):
        return (distance(self, point) < self.radius) and (self.start_angle <= heading(self, point) <= self.end_angle)

    def __getitem__(self, key):
        if key == 0:
            return self.lat
        elif key == 1:
            return self.lon
        else:
            raise IndexError

class Opti:
    """
    Opti
    """

    def __init__(self, dist, legs, points, angles):
        self.distance = dist
        self.legs = legs
        self.points = points
        self._angles = angles


class Point(geometry.Point):
    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError

    def serialize(self):
        return {
            'lat':self.x, 
            'lon':self.y, 
            'altitude':self.z, 
            'agl':self.agl if hasattr(self, 'agl') else None
            }
