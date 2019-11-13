import base64
import json
import logging
import os
from datetime import datetime, time, timedelta
from igclib.utils.timeop import next_second

import numpy as np
from igclib.constants import DEBUG
from igclib.model.geo import Opti, Point, Turnpoint
from igclib.parsers import pwca, xctrack
from igclib.utils.json_encoder import ComplexEncoder
from igclib.utils.optimizer import optimize


class Task():
    """
    Args:
        task_file (str): Path to or base64 representation of a task file.
    Raises:
        NotImplementedError: If the task could not be parsed.
    """

    def __init__(self, task_file):

        task = None
        # try to base64 decode the task
        if not os.path.isfile(task_file):
            try:
                task_file = base64.b64decode(task_file)
            except TypeError:
                logging.debug(f'Task is not base64')

        # try to parse with every implemented format, raise if no match
        for task_format in [xctrack.XCTask, pwca.PWCATask]:
            try:
                task = task_format(task_file)
                break
            except KeyError:
                logging.debug(f'Task format does not fit into {task_format}')
        if task is None:
            raise NotImplementedError('Task format not recognized')
        
        self.date = task.date
        self.open = task.open if 'open' in task.__dict__ else time(task.start.hour - 1, task.start.minute, task.start.second)
        self.start = task.start
        self.stop = task.stop

        self.takeoff = task.takeoff
        self.sss = task.sss
        self.turnpoints = task.turnpoints
        self.ess = task.ess

        self.opti = optimize(self.takeoff, self.turnpoints)

    def _timerange(self, start=None, stop=None):
        current = start if start is not None else self.open
        stop = stop if stop is not None else self.stop
        while current < stop:
            yield current
            current = next_second(current)
    
    def _update_tag_times(self, times):
        for turnpoint, contender in zip(self.turnpoints, times):
            if turnpoint.first_tag is None or contender < turnpoint.first_tag:
                turnpoint.first_tag = contender


    def validate(self, flight):
        remaining_turnpoints = self.turnpoints.copy()
        goal_distances = {}
        tag_times = []
        optimizer_init_vector = None
        
        for timestamp, point in flight.points.items():

            # race has not started yet
            if timestamp < self.start:
                opti = optimize(point, remaining_turnpoints, prev_opti=optimizer_init_vector)
                goal_distances[timestamp] = opti.distance
                optimizer_init_vector = opti.angles
                continue

            if len(remaining_turnpoints) > 0:
                opti = optimize(point, remaining_turnpoints, prev_opti=optimizer_init_vector)
                goal_distances[timestamp] = opti.distance
                optimizer_init_vector = opti.angles
                
                if point.close_enough(remaining_turnpoints[0]):
                    tag_times.append(timestamp)
                    del remaining_turnpoints[0]
                    logging.debug(f'{flight.pilot_id} passed TP at {timestamp}, {len(remaining_turnpoints)} wp remaining')

            # in goal, fill with zeros until landing
            else:
                goal_distances[timestamp] = 0
            
        return flight.pilot_id, goal_distances, tag_times

    def to_json(self):
        return self.__dict__
    
    def optimized(self, output=None):
        if output is not None:
            with open(output, 'w') as f:
                json.dump(self.opti, f, cls=ComplexEncoder)
        else:
            print(json.dumps(self.opti, cls=ComplexEncoder))

    def __len__(self):
        return int(self.opti.distance)
