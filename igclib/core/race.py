import json
import logging
import multiprocessing
#multiprocessing.set_start_method('spawn', True)  #-> DEBUG MULTIPROCESS
import os
import shutil
import sys
import zipfile
from glob import glob
from collections import defaultdict

import numpy as np
#import seaborn as sns
from igclib.core import BaseObject
from igclib.serialization.json_encoder import ComplexEncoder
from igclib.core.flight import Flight
from igclib.core.pilot_features import PilotFeatures
from igclib.core.ranking import Ranking
from igclib.core.task import Task
from igclib.crawlers.flight_crawler import FlightCrawler
from igclib.time.timeop import sub_times
from scipy.signal import savgol_filter
from tqdm import tqdm


class Race(BaseObject):
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
            self.load(path)
            if not self.validated and self._validate:
                self.validate_flights()

        # or build it from arguments
        else:
            # by parsing the task file or b64 to create a Task
            self.task = Task(task)

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
        return len([_ for _ in self.snapshots()])

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
                self.task.update_tag_times(tag_times)

                if self._progress == 'ratio':
                    print(f'{steps/self.n_pilots:.0%}', file=sys.stderr, flush=True)
                    steps += 1

        self.validated = True

    def __str__(self):
        return f'{self.n_pilots} pilots - {len(self.task)}m task - start at {self.task.start} - deadline at {self.task.stop}'

    def __repr__(self):
        return str(self)

    def watch(self, pilot_id, output, sparse=1):
        """
        Convention : If a GroupRelation feature is > 0, it means that the original pilot is
        in a better position than the other pilot in the group.
        This means that :

        * delta_altitude > 0 : original pilot is higher 
        * delta_distance > 0 : original pilot closer to goal 

        Args:
            pilot_id (list(str)): List of IDs of the pilots being watched, or ['all']
        """
        if len(pilot_id) == 1 and pilot_id[0] == 'all':
            pilot_id = list(self.flights.keys())
        else:
            pilot_id = list(filter(lambda x: x in self.flights, pilot_id))

        series = {p: {'altitude': [], 'distance': []} for p in pilot_id}
        series['timestamps'] = []

        steps = 1
        total = len(self)
        for timestamp, snapshot in tqdm(self.snapshots(), total=len(self), disable=self._progress != 'gui'):

            series['timestamps'].append(timestamp)
            altitudes = np.array([p.altitude for p in snapshot.values()])
            goal_distances = np.array([p.goal_distance for p in snapshot.values()])

            for pilot in pilot_id:
                # FIXME why do some pilots are in pilot_id but not in snapshot at this point ?
                if pilot in snapshot:
                    delta_altitude = snapshot[pilot].altitude - altitudes.mean()
                    delta_distance = goal_distances.mean() - snapshot[pilot].goal_distance
                    series[pilot]['altitude'].append(delta_altitude)
                    series[pilot]['distance'].append(delta_distance)

            if self._progress == 'ratio':
                print(f'{steps/total:.0%}', file=sys.stderr, flush=True)
                steps += 1

        for key in series:
            if key == 'timestamps':
                series[key] = series[key][::sparse]
            else:
                for feature in series[key]:
                    series[key][feature] = savgol_filter(series[key][feature], 121, 1)[::sparse]

        if isinstance(output, list):
            for out in output:
                if out == '-':
                    print(json.dumps(series, cls=ComplexEncoder))
                elif out.endswith('.json'):
                    with open(out, 'w', encoding='utf8') as f:
                        json.dump(series, f, cls=ComplexEncoder, ensure_ascii=False, indent=4)

    def snapshots(self, start=None, stop=None):
        """
        Generates snapshots of the race at each second between start and stop
        """
        for timestamp in self.task._timerange(start, stop):
            if self[timestamp] != {}:
                yield timestamp, self[timestamp]

    def serialize(self):
        """Serializes the race object to be written to a JSON file"""
        snaps = {str(_[0]): _[1] for _ in self.snapshots()}
        props = {'n_snaps': len(snaps)}
        return dict(properties=props, task=self.task, ranking=self.ranking, race=snaps)
