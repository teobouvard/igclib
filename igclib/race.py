import logging
import math
import os
import sys
from datetime import time
from glob import glob

from tqdm import tqdm

from flight import Flight
from pilot_features import PilotFeatures
from task import Task


class Race():

    def __init__(self, tracks_dir, task_file):

        tracks = glob(os.path.join(tracks_dir, '*.igc'))
        self.n_pilots = len(tracks)
        self.task = Task(task_file)
        self.flights = {os.path.basename(x).split('.')[0]:Flight(x) for x in tqdm(tracks, desc='reading tracks')}
        
        for pilot, flight in tqdm(self.flights.items(), desc='validating flights'):
            self.task.validate(flight)

        # cache pilot features to compute them only once for each pilot
        # maybe this is not a good idea ?
        self.pilot_features = {}

    def __getitem__(self, time_point):
        """
        Get a snapshot of the race at a given time
        """
        return {pilot_id:flight[time_point] for pilot_id, flight in self.flights.items() if flight[time_point] is not None}
    

    def __len__(self):
        return len([_ for _ in self.snapshots()])


    def __str__(self):
        s = '{} pilots - '.format(self.n_pilots)
        s += '{}km task - '.format(len(self.task))
        s += 'start at {} - '.format(self.task.start)
        s += 'deadline at {} - '.format(self.task.stop)
        return s
    

    def __repr__(self):
        return str(self)


    def get_pilot_features(self, pilot_id, start=None, stop=None):
        """
        Extract pilot features for the whole task
        """
        # check if pilot is in flight during the race
        if pilot_id not in self.flights:
            raise KeyError('Pilot {} is not in the race'.format(pilot_id))
        
        # check if pilot is in feature cache TODO and range is equal or smaller !
        if pilot_id in self.pilot_features:
            return self.pilot_features[pilot_id]

        features = {}
        
        for timestamp, snapshot in tqdm(self.snapshots(start, stop), desc='extracting features', total=len(self)):
            if pilot_id not in snapshot:
                logging.info('Pilot {} has no track at time {}'.format(pilot_id, timestamp))

            else:
                features[timestamp] = PilotFeatures(pilot_id, timestamp, snapshot)
        
        # cache pilot features for future access
        self.pilot_features[pilot_id] = features

        return features


    def snapshots(self, start=None, stop=None):
        """
        Generator of snapshots of the race at each second between start and stop
        """
        for timestamp in self.task.timerange(start, stop):
            if self[timestamp] != {}:
                yield timestamp, self[timestamp]
