import math

import numpy as np
from igclib.constants import MIN_TURNPOINTS_DISTANCE
from igclib.constants import distance_computation as distance
from igclib.model.geo import Opti, Turnpoint
from scipy.optimize import basinhopping, minimize

from geolib import get_heading, get_offset

def optimize(position, waypoints, prev_opti=None):
    x0 = np.zeros(len(waypoints)) if prev_opti is None else prev_opti
    result = minimize(tasklen, x0, args=(position, waypoints), tol=10)

    distances = []
    fast_waypoints = [Turnpoint(position.lat, position.lon)]

    for theta, wp in zip(result.x, waypoints):
        fp_lat, fp_lon = get_offset(wp.lat, wp.lon, wp.radius, theta)
        distances.append(distance(fp_lat, fp_lon, fast_waypoints[-1].lat, fast_waypoints[-1].lon))
        fast_waypoints.append(Turnpoint(fp_lat, fp_lon))

    return Opti(sum(distances), distances, fast_waypoints, result.x)

def tasklen(t, position, waypoints):
    dist = 0
    last_lat = position.lat
    last_lon = position.lon

    for theta, wp in zip(t, waypoints):
        lat_dest, lon_dest = get_offset(wp.lat, wp.lon, wp.radius, theta)
        dist += distance(lat_dest, lon_dest, last_lat, last_lon)
        last_lat, last_lon = lat_dest, lon_dest

    return dist