import json
import logging
from datetime import datetime, time, timedelta

from igclib.constants import DEBUG
from igclib.constants import distance_computation as distance
from igclib.model.geo import Opti, Point, Turnpoint
from igclib.parsers import xctrack, pwca
from igclib.utils.json_encoder import ComplexEncoder
from igclib.utils.optimizer import optimize

# fast distance computations do not validate turnpoints without tolerances
TOLERANCE = 0.05

class Task():
    """
    Args:
        task_file (str): Path to a task file or string representation of the task.
    Raises:
        NotImplementedError: If the task could not be parsed.
    """

    # TODO autoparse task type
    def __init__(self, task_file):

        # try to parse with every implemented format, raise if no match
        task = None
        for task_format in [xctrack.XCTask, pwca.PWCATask]:
            try:
                task = task_format(task_file)
                break
            except KeyError:
                logging.debug(f'Task file does not fit into {task_format}')
        if task is None:
            raise NotImplementedError(f'{task_type} tasks are not yet supported')

        self.start = task.start
        self.stop = task.stop if task.stop > self.start else time(23, 59, 59)

        self.takeoff = task.takeoff
        self.sss = task.sss
        self.turnpoints = task.turnpoints
        self.ess = task.ess
        self.opti = optimize(self.takeoff, self.turnpoints)

    def _timerange(self, start=None, stop=None):
        start = start if start is not None else self.start
        stop = stop if stop is not None else self.stop

        # all this mess is necessary because you can't add datetime.time objects, which are used by the aerofiles parser
        current = datetime(1, 1, 1, start.hour, start.minute, start.second)
        stop = datetime(1, 1, 1, stop.hour, stop.minute, stop.second)

        while current < stop:
            yield current.time()
            current += timedelta(seconds=1)


    def validate(self, flight):
        remaining_turnpoints = self.turnpoints.copy()
        goal_distances = {}
        optimizer_init_vector = None
        
        for timestamp, point in flight.points.items():

            # race has not started yet
            if timestamp < self.start:
                opti = optimize(point, remaining_turnpoints, optimizer_init_vector)
                goal_distances[timestamp] = opti.distance
                optimizer_init_vector = opti.angles
                continue

            if len(remaining_turnpoints) > 0:
                opti = optimize(point, remaining_turnpoints, optimizer_init_vector)
                goal_distances[timestamp] = opti.distance
                optimizer_init_vector = opti.angles
                
                if self._close_enough(point, remaining_turnpoints[0]):
                    del remaining_turnpoints[0]
                    logging.info('Turnpoint passed at {}, {} wp remaining'.format(timestamp, len(remaining_turnpoints)))

            # in goal, fill zeros until landing
            else:
                goal_distances[timestamp] = 0
            
        return flight.pilot_id, goal_distances

    def to_json(self):
        return json.dumps(self.opti, cls=ComplexEncoder)

    def __len__(self):
        return int(self.opti.distance)

    @staticmethod
    def _close_enough(pos, wpt):
        return True if abs(distance(pos.lat, pos.lon, wpt.lat, wpt.lon) - wpt.radius) < wpt.radius*TOLERANCE else False

    @staticmethod
    def _concentric_case(wptA, wptB):
        return True if wptA.lat == wptB.lat and wptA.lon == wptB.lon and wptB.radius < wptA.radius else False