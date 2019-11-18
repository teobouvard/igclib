import json
import math
import sys

import numpy as np
from igclib.constants import OPTIMIZER_PRECISION
from igclib.model.geo import Opti, Point, Turnpoint
from igclib.utils.json_encoder import ComplexEncoder
from scipy.optimize import minimize

from geolib import destination, distance, heading


def optimize(position, waypoints, prev_opti=None, callback=False):
    x0 = np.zeros(len(waypoints)) if prev_opti is None else prev_opti
    result = minimize(tasklen, x0, args=(position, waypoints), tol=OPTIMIZER_PRECISION, callback=lambda x:log_opti(x, waypoints) if callback else None)

    distances = []
    fast_waypoints = [Turnpoint(position.lat, position.lon)]

    for theta, wp in zip(result.x, waypoints):
        fp_lat, fp_lon = destination(wp.lat, wp.lon, wp.radius, theta)
        distances.append(distance(fp_lat, fp_lon, fast_waypoints[-1].lat, fast_waypoints[-1].lon))
        fast_waypoints.append(Turnpoint(fp_lat, fp_lon))

    return Opti(sum(distances), distances, fast_waypoints, result.x)

def tasklen(angles, position, waypoints):
    dist = 0
    last_lat = position.lat
    last_lon = position.lon

    for theta, wp in zip(angles, waypoints):
        lat_dest, lon_dest = destination(wp.lat, wp.lon, wp.radius, theta)
        dist += distance(lat_dest, lon_dest, last_lat, last_lon)
        last_lat, last_lon = lat_dest, lon_dest

    return dist

def log_opti(angles, waypoints):
    route = []
    for theta, wp in zip(angles, waypoints):
        lat, lon = destination(wp.lat, wp.lon, wp.radius, theta)
        route.append(Point(lat, lon))
    json_route = json.dumps(route, cls=ComplexEncoder)
    print(json_route, file=sys.stderr, flush=True)
