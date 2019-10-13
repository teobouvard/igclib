class Turnpoint():

    __slots__ = ['lat', 'lon', 'radius', 'altitude', 'name', 'desc', 'role', 'direction']

    def __init__(self, lat, lon, radius=None, altitude=None, name=None, desc=None, role=None, direction=None):
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.altitude = altitude
        self.name = name
        self.desc = desc
        self.role = role
        self.direction = direction
        

class Point():

    __slots__ = ['lat', 'lon', 'altitude', 'goal_distance']

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

class Opti():

    __slots__ = ['distance', 'legs', 'points']

    def __init__(self, distance, legs, points):
        self.distance = distance
        self.legs = legs
        self.points = points