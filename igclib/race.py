import os
from glob import glob

from flight import Flight
from task import Task


class Race():

    def __init__(self, tracks_dir, task_file=None):
        
        tracks = glob(os.path.join(tracks_dir, '*.igc'))
        self.flights = {os.path.basename(x).split('.')[0]:Flight(x) for x in tracks}
        self.task = Task(task_file)

    def pilot_features(self, pilot_id):
        pilot_flight = self.flights[pilot_id]
        