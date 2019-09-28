import os
from glob import glob
from datetime import time

from flight import Flight
from task import Task

class Race():

    def __init__(self, tracks_dir, task_file=None):
        tracks = glob(os.path.join(tracks_dir, '*.igc'))
        self.flights = {os.path.basename(x).split('.')[0]:Flight(x) for x in tracks}
        self.task = Task(task_file)

    def __getitem__(self, time_point):
        """
        Get a snapshot of the race at a certain time
        """
        return {pilot_id:flight[time_point] for pilot_id, flight in self.flights.items()}

    def pilot_features(self, pilot_id):
        """
        Extract pilot features for the whole task
        """
        if pilot_id not in self.flights:
            raise KeyError('Pilot {} is not in the race'.format(pilot_id))
        
        for timestamp, snapshot in self.snapshot_generator():
            if snapshot[pilot_id] is not None:
                print(snapshot[pilot_id]['gps_alt'])
            else:
                print('Pilot {} has no track at time {}'.format(pilot_id, timestamp))

    def snapshot_generator(self, start=None, stop=None):
        """
        Generates a snapshot of the race at each second between start and stop
        """
        for timestamp in self.task.timerange(start, stop):
            yield timestamp, self[timestamp]