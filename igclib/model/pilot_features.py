from igclib.constants import IGC_ALTITUDE
from igclib.model.group_relation import GroupRelation

class PilotFeatures():

    def __init__(self, pilot_id, timestamp, snapshot):
        self.pilot_id = pilot_id
        self.timestamp = timestamp
        self.altitude = snapshot[pilot_id][IGC_ALTITUDE]
        self.position = (snapshot[pilot_id]['lat'], snapshot[pilot_id]['lon'])
        self.goal_distance = snapshot[pilot_id]['goal_dist']
        self.group_relation = GroupRelation(pilot_id, snapshot)
