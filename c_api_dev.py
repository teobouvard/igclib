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

pos = (30, 30)
wp0 = Waypoint(30.5, 30.5, 4)
wp1 = Waypoint(30, 30, 2)
wpts = [wp0, wp1]

#print(haversine(30, 30, 30.5, 30.5))
dist, fwp, legs = optimize(pos, wpts)
print(dist)
print(fwp[0].lon)

