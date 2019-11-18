import json
import logging
import multiprocessing
#multiprocessing.set_start_method('spawn', True)
import os
import pickle
import sys
import zipfile
from datetime import datetime, time
from glob import glob

import numpy as np
import seaborn as sns
from igclib.constants import DEBUG
from igclib.crawlers.flight_crawler import FlightCrawler
from igclib.model.flight import Flight
from igclib.model.pilot_features import PilotFeatures
from igclib.model.task import Task
from igclib.utils.json_encoder import ComplexEncoder
from igclib.utils.timeop import sub_times
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter
from tqdm import tqdm


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
        path (str): The path of a previously saved Race instance.

    Attributes:
        n_pilots (int) : The number of pilots in the Race.
        flights (dict [str, Flight]) : A collection of Flights indexed by pilot ID.
        task (Task) : The Task instance of the Race.
    """

    def __init__(self, tracks_dir=None, task_file=None, validate=True, path=None, progress='gui'):
        self._validate = validate
        self._progress = progress
        
        # load race from pickle
        if path is not None:
            self._load(path)
            if not self.validated and self._validate:
                self._validate_flights()

        # or build it from arguments
        else:
            self._progress = progress
            self.task = Task(task_file)

            if tracks_dir is None:
                try:
                    tracks_dir = FlightCrawler(self.task, progress=self._progress).directory
                except ValueError:
                    logging.error('This task format does not support flight crawling yet, provide --flights directory.')

            self._parse_flights(tracks_dir)

            if self._validate:
                self._validate_flights()
            else:
                self.validated = False


    def __getitem__(self, time_point):
        """
        Returns a snapshot of the race at a given time

        Arguments:
            time_point (~datetime.time) : The second at which the snapshot is taken
        """
        snaps = {}
        for pilot_id, flight in self.flights.items():
            if flight[time_point] is not None:
                snaps[pilot_id] = flight[time_point]
            else:
                if time_point < flight._first_point['timestamp']:
                    snaps[pilot_id] = flight._first_point['point']
                elif time_point > flight._last_point['timestamp']:
                    snaps[pilot_id] = flight._last_point['point']
                else:
                    raise ValueError(f'Something terribly wrong happened with the tracklog of pilot {pilot_id}')
        return snaps


    def __len__(self):
        return len([_ for _ in self._snapshots()])


    def _parse_flights(self, tracks_dir):
        if zipfile.is_zipfile(tracks_dir):
            archive = zipfile.ZipFile(tracks_dir)
            archive.extractall(path='/tmp')
            tracks_dir = os.path.join('/tmp', os.path.splitext(os.path.basename(tracks_dir))[0])

        if os.path.isdir(tracks_dir):
            tracks = glob(os.path.join(tracks_dir, '*.igc'));
            if len(tracks) == 0:
                raise ValueError('Flight directory does not contain any igc files')
        else:
            raise ValueError(f'{tracks_dir} is not a directory')

        self.n_pilots = len(tracks)
        self.flights = {}

        steps = 1
        for x in tqdm(tracks, desc='reading tracks', disable=self._progress!='gui'):
            pilot_id = os.path.splitext(os.path.basename(x))[0]
            self.flights[pilot_id] = Flight(x)

            if self._progress == 'ratio':
                print(f'{steps}/{self.n_pilots}', file=sys.stderr, flush=True)
                steps +=1

    
    def _validate_flights(self):
        """Computes the validation of each flight on the race"""
        if DEBUG == True:
            for pilot_id, flight in tqdm(self.flights.items(), desc='validating flights', total=self.n_pilots):
                self.task.validate(flight)

        else:
            with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
                steps = 1

                # we can't just map(self.task.validate, self.flights) because instance attributes updated in subprocesses are not copied back on join 
                for pilot_id, goal_distances, tag_times in tqdm(p.imap_unordered(self.task.validate, self.flights.values()), desc='validating flights', total=self.n_pilots, disable=self._progress!='gui'):
                    
                    # update goal distances of flight points
                    for timestamp, point in self.flights[pilot_id].points.items():
                        point.goal_distance = goal_distances[timestamp]

                    # compute race time for pilot, read list in reverse because ESS is more likely near the end
                    self.flights[pilot_id].race_distance = len(self.task) - min(goal_distances.values())
                    self.flights[pilot_id]._last_point['point'].goal_distance =  min(goal_distances.values())
                    
                    # compute race time for pilot, read list in reverse because ESS is more likely near the end
                    if len(tag_times) == len(self.task.turnpoints):
                        for i, turnpoint in enumerate(self.task.turnpoints[::-1]):
                            if turnpoint.role == 'ESS':
                                race_time = sub_times(tag_times[-(i+1)], self.task.start)
                                self.flights[pilot_id].race_time = race_time
                                logging.debug(f'{pilot_id} SS : {race_time}')

                    # update tag_times of turnpoints
                    self.task._update_tag_times(tag_times)
                    
                    if self._progress == 'ratio':
                        print(f'{steps}/{self.n_pilots}', file=sys.stderr, flush=True)
                        steps +=1
            
            # number of pilots in goal TODO TIME THIS
            self.in_goal = []
            for pilot_id, flight in self.flights.items():
                for point in list(flight.points.values())[::-1]:
                    if point.goal_distance == 0:
                        self.in_goal.append(pilot_id)
                        break

            logging.info(f'{str(len(self.in_goal))} pilots in goal')


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
        steps = 1
        total = len(self)
        for timestamp, snapshot in tqdm(self._snapshots(start, stop), desc='extracting features', total=len(self), disable=self._progress!='gui'):
            if pilot_id not in snapshot:
                logging.debug(f'Pilot {pilot_id} has no track at time {timestamp}')
            else:
                features[timestamp] = PilotFeatures(pilot_id, timestamp, snapshot)

            if self._progress == 'ratio':
                print(f'{steps}/{total}', file=sys.stderr, flush=True)
                steps +=1

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
            'timestamps' : timestamps,
            'delta_altitudes' : smoothed_altitudes,
            'delta_distances' : smoothed_distances,
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
        """
        if output is None:
            logging.info('Race was not saved because you did not specify an output file')

        elif output.endswith('.pkl'):
            with open(output, 'wb') as f:
                to_save = {x:y for x, y in self.__dict__.items() if not x.startswith('_')}
                pickle.dump(to_save, f)

        elif output.endswith('.json'):
            with open(output, 'w', encoding='utf8') as f:
                json.dump(self._serialize(), f, cls=ComplexEncoder, ensure_ascii=False, indent=4)

        elif output.endswith('.igclib'):
            path = os.path.dirname(output)
            filename = os.path.basename(output)
            canonical = os.path.splitext(filename)[0]
            json_output = os.path.join(path, f'{canonical}.json')
            pkl_output = os.path.join(path, f'{canonical}.pkl')
            self.save(output=json_output)
            self.save(output=pkl_output)

        else:
            raise NotImplementedError('Supported output files : .json, .pkl, .igclib')
            
    def _serialize(self):
        snaps = {str(_[0]):_[1] for _ in self._snapshots()}
        ranking = {}
        if self._validate:
            for pilot_id, flight in self.flights.items():
                ranking[pilot_id] = {
                    'name' : str(flight),
                    'id': pilot_id,
                    'distance' : flight.race_distance,
                    'time' : flight.race_time
                }
            ranking = sorted(ranking.values(), key=lambda x: (-x['distance'], x['time']))
        return dict(task=self.task, ranking=ranking, race=snaps)

    def _load(self, path):
        """
        Loads the race instance from a pickle file
        """
        if path.endswith('.pkl'):
            with open(path, 'rb') as f:
                self.__dict__.update(pickle.load(f))
        else:
            raise ValueError('You can only load a race from a .pkl file')
