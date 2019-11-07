import math

import numpy as np
from igclib.constants import OPTIMIZER_PRECISION
from igclib.model.geo import Opti, Turnpoint
from scipy.optimize import minimize

from geolib import destination, distance, heading


def optimize(position, waypoints, correction, prev_opti=None):
    x0 = np.zeros(len(waypoints)) if prev_opti is None else prev_opti
    result = minimize(tasklen, x0, args=(position, waypoints, correction), tol=OPTIMIZER_PRECISION)

    distances = []
    fast_waypoints = [Turnpoint(position.lat, position.lon)]

    for theta, wp in zip(result.x, waypoints):
        fp_lat, fp_lon = destination(wp.lat, wp.lon, wp.radius, theta, correction[0], correction[1])
        distances.append(distance(fp_lat, fp_lon, fast_waypoints[-1].lat, fast_waypoints[-1].lon, correction[0], correction[1]))
        fast_waypoints.append(Turnpoint(fp_lat, fp_lon))

    return Opti(sum(distances), distances, fast_waypoints, result.x)

def tasklen(angles, position, waypoints, correction):
    dist = 0
    last_lat = position.lat
    last_lon = position.lon

    for theta, wp in zip(angles, waypoints):
        lat_dest, lon_dest = destination(wp.lat, wp.lon, wp.radius, theta, correction[0], correction[1])
        dist += distance(lat_dest, lon_dest, last_lat, last_lon, correction[0], correction[1])
        last_lat, last_lon = lat_dest, lon_dest

    return dist
