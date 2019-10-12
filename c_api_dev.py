from geolib import optimize, haversine

class Position():
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

class Waypoint():
    def __init__(self, lat, lon, radius):
        self.lat = lat
        self.lon = lon
        self.radius = radius

pos = (36.12, -86.67)
wp0 = Waypoint(33.94, -118.4, 4000)
wp1 = Waypoint(11, 13, 2000)
wpts = [wp0]#, wp1]

#print(haversine(36.12, -86.67, 33.94, -118.4))
print(optimize(pos, wpts))

