import math
import os
import sys
from datetime import time
from glob import glob

from geopy import distance
from tqdm import tqdm

from flight import Flight
from task import Task

LOG_LEVEL = 0

IGC_ALTITUDE = 'gps_alt'
IGC_LAT = 'lat'
IGC_LON = 'lon'

class Race():

    def __init__(self, tracks_dir, task_file=None):

        tracks = glob(os.path.join(tracks_dir, '*.igc'))
        self.flights = {os.path.basename(x).split('.')[0]:Flight(x) for x in tqdm(tracks, desc='reading tracks')}
        self.task = Task(task_file)


    def __getitem__(self, time_point):
        """
        Get a snapshot of the race at a given time
        """

        return {pilot_id:flight[time_point] for pilot_id, flight in self.flights.items() if flight[time_point] is not None}
    

    def __len__(self):
        return len([_ for _ in self.snapshot_generator()])


    def pilot_features(self, pilot_id, start=None, stop=None):
        """
        Extract pilot features for the whole task
        """

        if pilot_id not in self.flights:
            raise KeyError('Pilot {} is not in the race'.format(pilot_id))

        features = {
            'timestamp' : [],
            'altitude' : [],
            'goal_dist' : [],
            'goal_gr' : [],
            'group_relation' : [],
        }
        
        for timestamp, snapshot in tqdm(self.snapshot_generator(start, stop), desc='extracting features', total=len(self)):
            if pilot_id not in snapshot:
                if LOG_LEVEL > 0:
                    print('Pilot {} has no track at time {}'.format(pilot_id, timestamp))
            else:
                features['timestamp'].append(timestamp)
                features['altitude'].append(snapshot[pilot_id][IGC_ALTITUDE])
                features['group_relation'].append(self.group_relation(pilot_id, snapshot))
        
        return features
    

    def group_relation(self, pilot_id, snapshot):
        group_relation = {}
        pilot_id_postition = (snapshot[pilot_id][IGC_LAT], snapshot[pilot_id][IGC_LON])

        for other_pilot, flight in snapshot.items():
            group_relation[other_pilot] = {}
            other_pilot_postition = (flight[IGC_LAT], flight[IGC_LON])

            group_relation[other_pilot]['delta_altitude'] = snapshot[pilot_id][IGC_ALTITUDE] - flight[IGC_ALTITUDE]
            group_relation[other_pilot]['distance'] = distance.geodesic(pilot_id_postition, other_pilot_postition, ellipsoid='WGS-84').meters

            if group_relation[other_pilot]['delta_altitude'] != 0:
                group_relation[other_pilot]['glide_ratio'] = group_relation[other_pilot]['distance']/group_relation[other_pilot]['delta_altitude'] 
                group_relation[other_pilot]['angle'] = math.atan(group_relation[other_pilot]['distance']/group_relation[other_pilot]['delta_altitude'])
            else:
                group_relation[other_pilot]['glide_ratio'] = sys.maxsize
                group_relation[other_pilot]['angle'] = math.pi/2

        return group_relation


    def snapshot_generator(self, start=None, stop=None):
        """
        Generate a snapshot of the race at each second between start and stop
        """

        for timestamp in self.task.timerange(start, stop):
            if self[timestamp] != {}:
                yield timestamp, self[timestamp]
