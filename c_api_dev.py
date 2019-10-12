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

pos = (0, 0)
wp1 = Waypoint(0.5, 0, 10000)
wp2 = Waypoint(0.5, 0.5, 10000)
wp3 = Waypoint(0, 0.5, 10000)
wp4 = Waypoint(0, 0, 100)
wpts = [wp1, wp2, wp3, wp4]

#print(haversine(30, 30, 30.5, 30.5))
dist, fwp, legs = optimize(pos, wpts)
print(dist)
print(fwp)
print(legs)

