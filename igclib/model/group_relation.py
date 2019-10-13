import math
import sys

from igclib.constants import distance_computation as distance


class GroupRelation():

    __slots__ = ['other_pilot_id', 'delta_altitude', 'delta_distance']

    def __init__(self, pilot_id, snapshot):
        self.other_pilot_id = []
        self.delta_altitude = []
        #self.raw_distance = []
        #self.glide_ratio = []
        self.delta_distance = []


        for other_pilot_id, flight in snapshot.items():

            delta_altitude = snapshot[pilot_id].altitude - flight.altitude
            delta_distance = flight.goal_distance - snapshot[pilot_id].goal_distance
            #raw_distance = distance(pilot_id_postition, other_pilot_postition).meters
            #glide_ratio = raw_distance/delta_altitude if delta_altitude > 0 else sys.maxsize
            # angle = math.atan(dist/delta_altitude) if delta_altitude != 0 else math.pi/2

            self.other_pilot_id.append(other_pilot_id)
            self.delta_altitude.append(delta_altitude)
            self.delta_distance.append(delta_distance)
            #self.raw_distance.append(raw_distance)
            #self.glide_ratio.append(glide_ratio)
