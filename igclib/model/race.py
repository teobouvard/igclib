import logging
import multiprocessing
import os
import pickle
from datetime import time
from glob import glob

from tqdm import tqdm

from igclib.model.flight import Flight
from igclib.model.pilot_features import PilotFeatures
from igclib.model.task import Task


class Race():

    def __init__(self, tracks_dir=None, task_file=None, n_jobs=1, path=None):

        if path is not None:
            self.load(path)
        
        else:
            tracks = glob(os.path.join(tracks_dir, '*.igc'))
            self.n_pilots = len(tracks)
            if self.n_pilots < 2:
                raise ValueError('Only one pilot, you call that a race ?')
            
            self.task = Task(task_file)
            self.flights = {os.path.basename(x).split('.')[0]:Flight(x) for x in tqdm(tracks, desc='reading tracks')}
            
            n_jobs = multiprocessing.cpu_count() if n_jobs == -1 else n_jobs
            with multiprocessing.Pool(n_jobs) as p:
                # we can't just map(self.task.validate, self.flights) because instance attributes updated in subprocesses are not copied back on join 
                for result in tqdm(p.imap_unordered(self.task.validate, self.flights.values()), desc='validating flights', total=self.n_pilots):
                    pilot_id = result[0]
                    goal_distances = result[1]
                    for timestamp, point in self.flights[pilot_id].points.items():
                        point['goal_dist'] = goal_distances[timestamp]

    def __getitem__(self, time_point):
        """
        Get a snapshot of the race at a given time
        """
        return {pilot_id:flight[time_point] for pilot_id, flight in self.flights.items() if flight[time_point] is not None}
    

    def __len__(self):
        return len([_ for _ in self.snapshots()])


    def __str__(self):
        s = '{} pilots - '.format(self.n_pilots)
        s += '{}m task - '.format(len(self.task))
        s += 'start at {} - '.format(self.task.start)
        s += 'deadline at {}'.format(self.task.stop)
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

        features = {}
        
        for timestamp, snapshot in tqdm(self.snapshots(start, stop), desc='extracting features', total=len(self)):
            if pilot_id not in snapshot:
                logging.debug('Pilot {} has no track at time {}'.format(pilot_id, timestamp))
            else:
                features[timestamp] = PilotFeatures(pilot_id, timestamp, snapshot)

        return features


    def snapshots(self, start=None, stop=None):
        """
        Generator of snapshots of the race at each second between start and stop
        """
        for timestamp in self.task.timerange(start, stop):
            if self[timestamp] != {}:
                yield timestamp, self[timestamp]

    def save(self, path):
        """
        Save the race instance to a pickle file
        """
        with open(path, 'wb') as f:
            pickle.dump(self.__dict__, f)
    
    def load(self, path):
        """
        Load the race instance from a pickle file
        """
        with open(path, 'rb') as f:
            self.__dict__.update(pickle.load(f)) 