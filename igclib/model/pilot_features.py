from igclib.constants import IGC_ALTITUDE
from igclib.model.group_relation import GroupRelation

class PilotFeatures():
    """[summary]
    """
    
    __slots__ = ['pilot_id', 'timestamp', 'position', 'group_relation']

    def __init__(self, pilot_id, timestamp, snapshot):
        self.pilot_id = pilot_id
        self.timestamp = timestamp
        self.position = snapshot[pilot_id]
        self.group_relation = GroupRelation(pilot_id, snapshot)
