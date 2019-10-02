from constants import IGC_ALTITUDE
from group_relation import GroupRelation

from utils.optimizer import Optimizer

class PilotFeatures():

    def __init__(self, pilot_id, timestamp, snapshot):
        self.pilot_id = pilot_id
        self.timestamp = timestamp
        self.altitude = snapshot[pilot_id][IGC_ALTITUDE]
        self.position = (snapshot[pilot_id]['lat'], snapshot[pilot_id]['lon'])
        self.goal_distance = Optimizer(self.position, snapshot[pilot_id]['remaining_waypoints']).distance_centers()
        self.goal_glide = None
        self.group_relation = GroupRelation(pilot_id, snapshot)
