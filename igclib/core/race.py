import json
import logging
import multiprocessing
#multiprocessing.set_start_method('spawn', True) #-> DEBUG MULTIPROCESS
import os
import pickle
import shutil
import sys
import zipfile
from datetime import datetime, time
from glob import glob

import numpy as np
#import seaborn as sns
from igclib.constants import DEBUG
from igclib.crawlers.flight_crawler import FlightCrawler
from igclib.core.flight import Flight
from igclib.core.ranking import Ranking
from igclib.core.pilot_features import PilotFeatures
from igclib.core.task import Task
from igclib.serialization.json_encoder import ComplexEncoder
from igclib.time.timeop import sub_times
from scipy.signal import savgol_filter
from tqdm import tqdm


class Race():
    """
    You can create a Race instance in two different ways :

    * Passing a tracks and a task, which creates a new Race object and validates all pilot flights.

        >>> r =  Race(tracks='tracks/', task='task.xctsk')

    * Passing a path to a previously saved Race, loading the saved instance (much faster than re-validating flights).

        >>> r =  Race(path='race.pkl')

    Keyword Arguments:
        tracks (str): A path to a directory or a zip file containing IGC tracks.
        task (str): A path to the task file or a base64 representation of the task.
        path (str): The path of a previously saved Race instance.

    Attributes:
        n_pilots (int) : The number of pilots in the Race.
        flights (dict [str, Flight]) : A collection of Flights indexed by pilot ID.
        task (Task) : The Task instance of the Race.
    """

    def __init__(self, tracks=None, task=None, validate=True, path=None, progress='gui'):
        self._validate = validate
        self._progress = progress

        # load race from pickle if path is given
        if path is not None:
            self._load(path)
            if not self.validated and self._validate:
                self.validate_flights()

        # or build it from arguments
        else:
            # by parsing the task file or b64 to create a Task
            self.task = Task(task, progress=self._progress)

            # trying to fetch the tracks if they were not provided by user
            if tracks is None:
                try:
                    tracks = FlightCrawler(self.task, progress=self._progress).directory
                except ValueError:
                    raise ValueError('This task format does not support flight crawling yet, provide --flights directory.')

            # reading the tracks and builiding the Flights objects
            self.parse_flights(tracks)

            # validating all Flights if necessary
            if self._validate:
                self.validate_flights()
            else:
                self.validated = False

        self.ranking = Ranking(self)

    def __getitem__(self, time_point):
        """
        Returns a snapshot of the race at a given time

        Arguments:
            time_point (~datetime.time) : The second at which the snapshot is taken
        """
        snap = {}
        for pilot_id, flight in self.flights.items():
            if flight[time_point] is not None:
                snap[pilot_id] = flight[time_point]
            else:
                if time_point < flight._first_point['timestamp']:
                    snap[pilot_id] = flight._first_point['point']
                elif time_point > flight._last_point['timestamp']:
                    snap[pilot_id] = flight._last_point['point']
        return snap

    def __len__(self):
        """Returns the number of snapshots between the earliest and the latest point from all flights."""
        return len([_ for _ in self._snapshots()])

    def parse_flights(self, tracks):
        """Populates flights attribute by parsing each igc file in tracks.

        Arguments:
            tracks (str) : Path to a directory or a zip file containing the igc files
        """
        tmp_file = None
        if zipfile.is_zipfile(tracks):
            tmp_file = os.path.join('/tmp', os.path.splitext(os.path.basename(tracks))[0])
            archive = zipfile.ZipFile(tracks)
            archive.extractall(path='/tmp')
            tracks = tmp_file
        if os.path.isdir(tracks):
            tracks = glob(os.path.join(tracks, '*.igc'))
        else:
            raise ValueError(f'{tracks} is not a directory or a zip file')

        self.n_pilots = len(tracks)
        if self.n_pilots == 0:
            raise ValueError('Flight directory does not contain any igc files')
        self.flights = {}

        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
            steps = 1
            for x in tqdm(p.imap_unordered(Flight, tracks), desc='reading tracks', total=self.n_pilots, disable=self._progress != 'gui'):
                self.flights[x.pilot_id] = x
                if self._progress == 'ratio':
                    print(f'{steps/self.n_pilots:.0%}', file=sys.stderr, flush=True)
                    steps += 1

        if tmp_file is not None:
            shutil.rmtree(tmp_file)

    def validate_flights(self):
        """Computes the validation of each flight on the race"""
        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
            steps = 1

            # we can't just map(self.task.validate, self.flights) because instance attributes updated in subprocesses are not copied back on join
            for pilot_id, goal_distances, tag_times in tqdm(p.imap_unordered(self.task.validate, self.flights.values()), desc='validating flights', total=self.n_pilots, disable=self._progress != 'gui'):

                # update goal distances of flight points
                for timestamp, point in self.flights[pilot_id].points.items():
                    point.goal_distance = goal_distances[timestamp]

                # compute race time for pilot, read list in reverse because ESS is more likely near the end
                self.flights[pilot_id].race_distance = len(self.task) - min(goal_distances.values())
                self.flights[pilot_id]._last_point['point'].goal_distance = min(goal_distances.values())

                # compute race time for pilot, read list in reverse because ESS is more likely near the end
                if len(tag_times) == len(self.task.turnpoints):
                    for i, turnpoint in enumerate(self.task.turnpoints[::-1]):
                        if turnpoint.role == 'ESS':
                            race_time = sub_times(tag_times[-(i + 1)], self.task.start)
                            self.flights[pilot_id].race_time = race_time
                            logging.debug(f'{pilot_id} SS : {race_time}')

                # update tag_times of turnpoints
                self.task._update_tag_times(tag_times)

                if self._progress == 'ratio':
                    print(f'{steps/self.n_pilots:.0%}', file=sys.stderr, flush=True)
                    steps += 1

        self.validated = True

    def __str__(self):
        return f'{self.n_pilots} pilots - {len(self.task)}m task - start at {self.task.start} - deadline at {self.task.stop}'

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
        steps = 1
        total = len(self)
        for timestamp, snapshot in tqdm(self._snapshots(start, stop), desc='extracting features', total=len(self), disable=self._progress != 'gui'):
            if pilot_id not in snapshot:
                logging.debug(f'Pilot {pilot_id} has no track at time {timestamp}')
            else:
                features[timestamp] = PilotFeatures(pilot_id, timestamp, snapshot)

            if self._progress == 'ratio':
                print(f'{steps/total:.0%}', file=sys.stderr, flush=True)
                steps += 1

        return features

    def pilot_schema_plot(self, pilot_id):
        """In dev !
        
        Args:
            pilot_id (str): ID of the pilot being studied
        """
        series = self.pilot_schema(pilot_id)

        sns.lineplot(x=series['timestamps'], y=series['smoothed_altitudes'])
        sns.lineplot(x=series['timestamps'], y=series['smoothed_distances'])
        plt.show()

    def pilot_schema(self, pilot_id, output=None):
        """In dev !
        
        Args:
            pilot_id (str): ID of the pilot being watched
        """
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

        series = {
            'timestamps': timestamps,
            'delta_altitudes': smoothed_altitudes,
            'delta_distances': smoothed_distances,
        }

        if output is None:
            return series
        elif output == '-':
            print(json.dumps(series, cls=ComplexEncoder))

    def _snapshots(self, start=None, stop=None):
        """
        Generates snapshots of the race at each second between start and stop
        """
        for timestamp in self.task._timerange(start, stop):
            if self[timestamp] != {}:
                yield timestamp, self[timestamp]

    def save(self, output):
        """
        Saves the race instance to a file specified by output
            * If output is a JSON file (.json), only a human-readable, serialized version of the race is written.
            * If output is a pickle file (.pkl), only a binary version of the race is written, which can be loaded by this class later.
            * If output is -, the JSON serialization is written to the standard output.

        Arguments:
            output (str) : Path to a file to which you want to write the output.
        """
        if type(output) == list:
            for out in output:
                self.save(out)
        elif output.endswith('.pkl'):
            with open(output, 'wb') as f:
                to_save = {x: y for x, y in self.__dict__.items() if not x.startswith('_')}
                pickle.dump(to_save, f)
        elif output.endswith('.json'):
            with open(output, 'w', encoding='utf8') as f:
                json.dump(self.serialize(), f, cls=ComplexEncoder, ensure_ascii=False)
        elif output == '-':
                print(json.dumps(self.serialize(), cls=ComplexEncoder, ensure_ascii=False))
        else:
            raise NotImplementedError('Supported outputs : .json, .pkl, -')

    def serialize(self):
        """Serializes the race object to be written to a JSON file"""
        snaps = {str(_[0]): _[1] for _ in self._snapshots()}
        props = {'n_snaps': len(snaps)}
        return dict(properties=props, task=self.task, ranking=self.ranking, race=snaps)

    def _load(self, path):
        """Loads the race instance from a pickle file"""
        if path.endswith('.pkl'):
            with open(path, 'rb') as f:
                self.__dict__.update(pickle.load(f))
        else:
            raise ValueError('You can only load a race from a .pkl file')
