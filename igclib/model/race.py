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
    """
    You can create a Race instance in two different ways :

    * Passing a tracks_dir and a task_file, which creates a new Race object and computes all pilot features.

        >>> r =  Race(tracks_dir='tracks/', task_file='task.xctsk')

    * Passing a path to a previously saved Race, loading the saved instance (much faster than recomputing features).

        >>> r =  Race(path='race.pkl')

    Keyword Arguments:
        tracks_dir (str): A path to the directory containing IGC tracks.
        task_file (str): A path to the task file.
        n_jobs (int): The number of processes to use when validating the tracks.
            The default value (-1) creates as many process as the CPU core count of the machine.
        path (str): The path of a previously saved Race instance.

    Attributes:
        n_pilots (int) : The number of pilots in the Race.
        flights (dict [str, Flight]) : A collection of Flight indexed by pilot ID.
        task (Task) : The Task instance of the Race.
    """

    def __init__(self, tracks_dir=None, task_file=None, n_jobs=-1, path=None):

        if path is not None:
            self._load(path)
        
        else:
            tracks = glob(os.path.join(tracks_dir, '*.igc'))
            self.n_pilots = len(tracks)
            
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
        Returns a snapshot of the race at a given time
        """
        return {pilot_id:flight[time_point] for pilot_id, flight in self.flights.items() if flight[time_point] is not None}
    

    def __len__(self):
        return len([_ for _ in self._snapshots()])


    def __str__(self):
        s = '{} pilots - '.format(self.n_pilots)
        s += '{}m task - '.format(len(self.task))
        s += 'start at {} - '.format(self.task.start)
        s += 'deadline at {}'.format(self.task.stop)
        return s
    

    def __repr__(self):
        return str(self)


    def get_pilot_features(self, pilot_id, start=None, stop=None):
        """Extracts pilot features

        Arguments:
            pilot_id (str) : The pilot identifier used as key in self.flights
        
        Keyword Arguments:
            start (~datetime.time, optional) : Lower bound of the retrieved features (default)
            stop (~datetime.time, optional) : Upper bound of the retrieved features
        
        Raises:
            KeyError: if pilot_id is not a key of self.flights dictionnary
        
        Returns:
            PilotFeatures: The pilot features from start to stop 
        """
        # check if pilot is in flight during the race
        if pilot_id not in self.flights:
            raise KeyError('Pilot {} is not in the race'.format(pilot_id))

        features = {}
        
        for timestamp, snapshot in tqdm(self._snapshots(start, stop), desc='extracting features', total=len(self)):
            if pilot_id not in snapshot:
                logging.debug('Pilot {} has no track at time {}'.format(pilot_id, timestamp))
            else:
                features[timestamp] = PilotFeatures(pilot_id, timestamp, snapshot)

        return features


    def _snapshots(self, start=None, stop=None):
        """
        Generator of snapshots of the race at each second between start and stop
        """
        for timestamp in self.task._timerange(start, stop):
            if self[timestamp] != {}:
                yield timestamp, self[timestamp]


    def save(self, path):
        """
        Save the race instance to a file specified by path
        """
        with open(path, 'wb') as f:
            pickle.dump(self.__dict__, f)
    

    def _load(self, path):
        """
        Load the race instance from a pickle file
        """
        with open(path, 'rb') as f:
            self.__dict__.update(pickle.load(f)) 