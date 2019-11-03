import json
import logging
import multiprocessing
import os
import pickle
import sys
from datetime import time
from glob import glob

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter
from tqdm import tqdm

from igclib.constants import DEBUG
from igclib.model.flight import Flight
from igclib.model.pilot_features import PilotFeatures
from igclib.model.task import Task
from igclib.utils.json_encoder import ComplexEncoder
from igclib.crawlers.flight_crawler import FlightCrawler


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
        flights (dict [str, Flight]) : A collection of Flights indexed by pilot ID.
        task (Task) : The Task instance of the Race.
    """

    #__slots__ = ['progress', 'n_pilots', 'flights', 'task']

    def __init__(self, tracks_dir=None, task_file=None, n_jobs=-1, path=None, progress='gui'):
        self.progress = progress

        # load race from pickle or build it from args
        if path is not None:
            self._load(path)
        else:
            self.task = Task(task_file)

            if tracks_dir is None:
                tracks_dir = self.crawl_flights()

            self._create_flights(tracks_dir)
            self._validate_flights(n_jobs)

    def crawl_flights(self):
        fc = FlightCrawler(self.task)
        return fc.directory


    def __getitem__(self, time_point):
        """
        Returns a snapshot of the race at a given time

        Arguments:
            time_point (~datetime.time) : The second at which the snapshot is taken
        """
        return {pilot_id:flight[time_point] for pilot_id, flight in self.flights.items() if flight[time_point] is not None}
    

    def __len__(self):
        return len([_ for _ in self._snapshots()])


    def _create_flights(self, tracks_dir):
        tracks = glob(os.path.join(tracks_dir, '*.igc'))
        if len(tracks) == 0:
            raise ValueError('Flight directory does not contain any igc files')
        self.n_pilots = len(tracks)
        self.flights = {}
        steps = 1
        for x in tqdm(tracks, desc='reading tracks', disable=self.progress!='gui'):
            pilot_id = os.path.basename(x).split('.')[0]
            self.flights[pilot_id] = Flight(x)
            if self.progress == 'ratio':
                print(f'{steps}/{self.n_pilots}', file=sys.stderr, flush=True)
                steps +=1

    
    def _validate_flights(self, n_jobs):
        """Computes the validation of each flight on the race"""
        if DEBUG == True:
                for pilot_id, flight in tqdm(self.flights.items(), desc='validating flights', total=self.n_pilots):
                    self.task.validate(flight)
        else:
            n_jobs = multiprocessing.cpu_count() if n_jobs == -1 else n_jobs
            with multiprocessing.Pool(n_jobs) as p:
                steps = 1
                # we can't just map(self.task.validate, self.flights) because instance attributes updated in subprocesses are not copied back on join 
                for pilot_id, goal_distances in tqdm(p.imap_unordered(self.task.validate, self.flights.values()), desc='validating flights', total=self.n_pilots, disable=self.progress!='gui'):
                    for timestamp, point in self.flights[pilot_id].points.items():
                        point.goal_distance = goal_distances[timestamp]
                    if self.progress == 'ratio':
                        print(f'{steps}/{self.n_pilots}', file=sys.stderr, flush=True)
                        steps +=1


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
        if pilot_id not in self.flights:
            raise KeyError('Pilot {} is not in the race'.format(pilot_id))

        features = {}
        
        for timestamp, snapshot in tqdm(self._snapshots(start, stop), desc='extracting features', total=len(self), file=sys.stdout):
            if pilot_id not in snapshot:
                logging.debug(f'Pilot {pilot_id} has no track at time {timestamp}')
            else:
                features[timestamp] = PilotFeatures(pilot_id, timestamp, snapshot)

        return features


    def pilot_schema(self, pilot_id):
        features = self.get_pilot_features(pilot_id)

        mean_altitudes = []
        mean_goal = []
        timestamps = list(features.keys())

        for feature in features.values():
            altitudes = np.array(feature.group_relation.delta_altitude)
            goal_distances = np.array(feature.group_relation.delta_distance)

            mean_altitudes.append(altitudes.mean())
            mean_goal.append(goal_distances.mean())
            
            
        smoothed_altitudes = savgol_filter(mean_altitudes, 121, 1)
        smoothed_distances = savgol_filter(mean_goal, 121, 1)
        gradient_altitudes = np.gradient(smoothed_altitudes)
        gradient_goal = np.gradient(smoothed_distances)

        _, ax = plt.subplots(2, 2, tight_layout=True, sharex=True)

        sns.lineplot(x=timestamps, y=smoothed_altitudes, ax=ax[0][0])
        sns.lineplot(x=timestamps, y=gradient_altitudes, ax=ax[1][0])
        sns.lineplot(x=timestamps, y=smoothed_distances, ax=ax[0][1])
        sns.lineplot(x=timestamps, y=gradient_goal, ax=ax[1][1])
        plt.show()


    def _snapshots(self, start=None, stop=None):
        """
        Generates snapshots of the race at each second between start and stop
        """
        for timestamp in self.task._timerange(start, stop):
            if self[timestamp] != {}:
                yield timestamp, self[timestamp]


    def save(self, path):
        """
        Saves the race instance to a file specified by path
        """
        if path is not None:
            with open(path, 'wb') as f:
                pickle.dump(self.__dict__, f)
        else:
            raise NotImplementedError('Provide an --output file')#dict(flights=self.flights)
            #s = json.dumps(dict(task=self.task), cls=ComplexEncoder)
            #print(s)
    

    def _load(self, path):
        """
        Loads the race instance from a pickle file
        """
        with open(path, 'rb') as f:
            self.__dict__.update(pickle.load(f)) 
