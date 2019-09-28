import os
from datetime import time
from glob import glob

from tqdm import tqdm

from flight import Flight
from task import Task

LOG_LEVEL = 0

IGC_ALTITUDE = 'gps_alt'

class Race():

    def __init__(self, tracks_dir, task_file=None):
        tracks = glob(os.path.join(tracks_dir, '*.igc'))
        self.flights = {os.path.basename(x).split('.')[0]:Flight(x) for x in tqdm(tracks, desc='reading tracks')}
        self.task = Task(task_file)

    def __getitem__(self, time_point):
        """
        Get a snapshot of the race at a certain time
        """
        return {pilot_id:flight[time_point] for pilot_id, flight in self.flights.items() if flight[time_point] }#is not None}

    def pilot_features(self, pilot_id):
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
        
        for timestamp, snapshot in tqdm(self.snapshot_generator(), desc='extracting features', total=len(self.flights.keys())):
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

        for pilot, flight in snapshot.items():
            if pilot != pilot_id:
                group_relation[pilot] = {'delta_altitude': snapshot[pilot_id][IGC_ALTITUDE] - flight[IGC_ALTITUDE]}

        return group_relation

    def snapshot_generator(self, start=None, stop=None):
        """
        Generates a snapshot of the race at each second between start and stop
        """
        for timestamp in self.task.timerange(start, stop):
            if self[timestamp] == {}:
                continue
            yield timestamp, self[timestamp]
