class PilotFeatures():
    """
    PilotFeatures

    Attributes:
        pilot_id (str) : The pilot's ID
        timestamp (~datetime.time) : The timestamp associated with the features.
        position (GeoPoint) : The current position of the pilot.
        group_relation (GroupRelation) : The current position of the pilot.
    """

    def __init__(self, pilot_id, timestamp, snapshot):
        self.pilot_id = pilot_id
        self.timestamp = timestamp
        self.position = snapshot[pilot_id]
        self.group_relation = GroupRelation(pilot_id, snapshot)


class GroupRelation():
    """
    GroupRelation

    Convention : If a GroupRelation feature is > 0, it means that the original pilot is 
    in a better position than the other pilot in the group.
    This means that :

    * delta_altitude > 0 : original pilot is higher 
    * delta_distance > 0 : original pilot closer to goal 

    Attributes:
        other_pilot_id (list [str]) : A list of IDs pilots being compared
        delta_altitude (list [float]) : The altitude differences.
        delta_distance (list [float]) : The goal distances differences.
    """

    def __init__(self, pilot_id, snapshot):
        self.other_pilot_id = []
        self.delta_altitude = []
        self.delta_distance = []

        for other_pilot_id, flight in snapshot.items():

            delta_altitude = snapshot[pilot_id].altitude - flight.altitude
            delta_distance = flight.goal_distance - snapshot[pilot_id].goal_distance

            self.other_pilot_id.append(other_pilot_id)
            self.delta_altitude.append(delta_altitude)
            self.delta_distance.append(delta_distance)
