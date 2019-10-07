from geographiclib.geodesic import Geodesic 
from constants import distance_computation as distance
from constants import MIN_TURNPOINTS_DISTANCE
import math

# Adapted from Julien Garcia's optimizer
# https://github.com/julien66/meteor-task-creator/blob/master/client/imports/betterOptimiser.js

def optimize(position, waypoints):
    optimized_distance, fast_waypoints = get_fast_waypoints(position, waypoints)
    return optimized_distance, fast_waypoints

def get_heading(wptA, wptB):
    return Geodesic.WGS84.Inverse(wptA['lat'], wptA['lon'], wptB['lat'], wptB['lon'], outmask=Geodesic.AZIMUTH)['azi1']

def get_offset(wpt, heading, dist):
    offset = Geodesic.WGS84.Direct(wpt['lat'], wpt['lon'], heading, dist)
    return dict(lat = offset['lat2'], lon = offset['lon2'], radius=wpt['radius'])

def get_fast_waypoints(position, waypoints):
    # Pushing current position as a fast waypoint
    fast_waypoints = [position]
    optimized_distance = 0

    if len(waypoints) < 2:
        fast_waypoints.append(waypoints[-1])
        optimized_distance += distance((position['lat'], position['lon']), (waypoints[-1]['lat'], waypoints[-1]['lon'])).meters
        return optimized_distance, fast_waypoints

    else:
        # Looping turnpoints
        for two, three in zip(waypoints[:], waypoints[1:]):
            one = fast_waypoints[-1]

            a_heading = get_heading(two, one)
            b_heading = get_heading(two, three)

            angle = b_heading - a_heading
            leg_heading = a_heading + 0.5 * angle
            a_distance = distance((one['lat'], one['lon']), (two['lat'], two['lon'])).meters
            b_distance = distance((two['lat'], two['lon']), (three['lat'], three['lon'])).meters


            if b_distance < MIN_TURNPOINTS_DISTANCE:
                min_leg_distance = two['radius']
                leg_heading = a_heading
            else:
                leg_distance = (2 * a_distance * b_distance * math.cos(math.radians(angle * 0.5))) / (a_distance + b_distance)
                min_leg_distance = min(leg_distance, two['radius'])

            fast_wp = get_offset(two, leg_heading, min_leg_distance)
            
            fast_waypoints.append(fast_wp)
            optimized_distance += distance((one['lat'], one['lon']), (fast_wp['lat'], fast_wp['lon'])).meters

        return optimized_distance, fast_waypoints