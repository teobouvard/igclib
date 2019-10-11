from geolib import optimize

class Position():
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

class Waypoint():
    def __init__(self, lat, lon, radius):
        self.lat = lat
        self.lon = lon
        self.radius = radius

pos = (22, 44)
wp0 = Waypoint(10, 12, 4000)
wp1 = Waypoint(11, 13, 2000)
wpts = [wp0, wp1]

print(optimize(pos, wpts))

