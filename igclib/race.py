import os
from glob import glob
from datetime import time

from flight import Flight
from task import Task

class Race():

    def __init__(self, tracks_dir, task_file=None):
        tracks = glob(os.path.join(tracks_dir, '*.igc'))
        self._flights = {os.path.basename(x).split('.')[0]:Flight(x) for x in tracks}
        self._task = Task(task_file)

    def __getitem__(self, time_point):
        """
        Get a snapshot of the race at a certain time
        """
        return {pilot_id:flight[time_point] for pilot_id, flight in self._flights.items()}

    def pilot_features(self, pilot_id, time_id):
        """
        pilot_id (str)  
        time_id (datetime.time)
        """
        position = self._flights[pilot_id][time_id]
        return position