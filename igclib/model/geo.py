class Turnpoint():
    """
    Turnpoint
    """

    #__slots__ = ['lat', 'lon', 'radius', 'altitude', 'name', 'desc', 'role', 'direction']

    def __init__(self, lat, lon, radius=None, altitude=None, name=None, desc=None, role=None, direction=None):
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.altitude = altitude
        self.name = name
        self.desc = desc
        self.role = role
        self.direction = direction
    
    def to_json(self):
        return dict(lat=self.lat, lon=self.lon, radius=self.radius)
        

class Point():
    """
    Point
    """

    #__slots__ = ['lat', 'lon', 'altitude', 'goal_distance']

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
    
        def to_json(self):
            return dict(lat=self.lat, lon=self.lon, altitude=self.altitude)


class Opti():
    """
    Opti
    """

    #__slots__ = ['distance', 'legs', 'points', 'angles']

    def __init__(self, distance=0, legs=[], points=[], angles=[]):
        self.distance = distance
        self.legs = legs
        self.points = points
        self.angles = angles

    def to_json(self):
        return dict(distance=self.distance, legs=self.legs, points=self.points)