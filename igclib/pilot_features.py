from constants import IGC_ALTITUDE
from group_relation import GroupRelation


class PilotFeatures():

    def __init__(self, pilot_id, timestamp, snapshot):
        self.pilot_id = pilot_id
        self.timestamp = timestamp
        self.altitude = snapshot[pilot_id][IGC_ALTITUDE]
        self.goal_distance = None
        self.goal_glide = None
        self.group_relation = GroupRelation(pilot_id, snapshot)
