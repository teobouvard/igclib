import math
import sys

from constants import IGC_ALTITUDE, IGC_LAT, IGC_LON
from constants import distance_computation as distance


class GroupRelation():

    def __init__(self, pilot_id, snapshot):
        self.other_pilot_id = []
        self.delta_altitude = []
        self.raw_distance = []
        self.glide_ratio = []

        pilot_id_postition = (snapshot[pilot_id][IGC_LAT], snapshot[pilot_id][IGC_LON])

        for other_pilot_id, flight in snapshot.items():
            other_pilot_postition = (flight[IGC_LAT], flight[IGC_LON])

            delta_altitude = snapshot[pilot_id][IGC_ALTITUDE] - flight[IGC_ALTITUDE]
            dist = distance(pilot_id_postition, other_pilot_postition).meters
            glide_ratio = dist/delta_altitude if delta_altitude > 0 else sys.maxsize
            # angle = math.atan(dist/delta_altitude) if delta_altitude != 0 else math.pi/2

            self.other_pilot_id.append(other_pilot_id)
            self.delta_altitude.append(delta_altitude)
            self.raw_distance.append(dist)
            self.glide_ratio.append(glide_ratio)