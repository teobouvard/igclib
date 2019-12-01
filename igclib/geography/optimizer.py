"""
This module provides optimizations for various objective methods.
    * Task distance optimization
    * XC flight distance maximization (hopefully soon)
"""

import numpy as np
from igclib.constants import OPTIMIZER_PRECISION
from igclib.geography import destination, distance, heading
from igclib.geography.geo import Opti, Point, Turnpoint
from scipy.optimize import minimize


def optimize(position, waypoints, prev_opti=None):
    x0 = np.zeros(len(waypoints)) if prev_opti is None else prev_opti
    result = minimize(tasklen, x0, args=(position, waypoints), tol=OPTIMIZER_PRECISION)

    distances = []
    fast_waypoints = [Turnpoint(position.lat, position.lon)]

    for theta, wp in zip(result.x, waypoints):
        fp_lat, fp_lon = destination(wp, wp.radius, theta)
        distances.append(distance(fp_lat, fp_lon, fast_waypoints[-1].lat, fast_waypoints[-1].lon))
        fast_waypoints.append(Turnpoint(fp_lat, fp_lon))

    return Opti(sum(distances), distances, fast_waypoints, result.x)


def tasklen(angles, position, waypoints):
    dist = 0
    last_lat = position.lat
    last_lon = position.lon

    for theta, wp in zip(angles, waypoints):
        lat_dest, lon_dest = destination(wp, wp.radius, theta)
        dist += distance(lat_dest, lon_dest, last_lat, last_lon)
        last_lat, last_lon = lat_dest, lon_dest

    return dist


def maximize_distance(flight):
    n_points = len(flight)
    x0 = np.array([0, 0.5, 0.9])
    result = minimize(triangle_length, x0, args=flight)

    return -result


def triangle_length(points, flight):
    total_distance = distance(flight[points[0]], flight[points[1]])
    total_distance += distance(flight[points[1]], flight[points[2]])
    total_distance += distance(flight[points[2]], flight[points[0]])
    return -total_distance
