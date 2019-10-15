import json
import logging
from datetime import datetime, time, timedelta

from matplotlib import pyplot as plt

from igclib.constants import DEBUG
from igclib.constants import distance_computation as distance
from igclib.model.geo import Opti, Point, Turnpoint
from igclib.parsers import xctrack
from igclib.utils.json_encoder import ComplexEncoder
from igclib.utils.optimizer import optimize

# fast distance computations do not validate turnpoints without tolerances
TOLERANCE = 0.05

class Task():
    """
    Args:
        task_file (str): Path to a task file.
        task_type (str, optional): Format of the task file. Defaults to 'xctrack'.
    
    Raises:
        NotImplementedError: If the task_type is not known.
    """

    # TODO autoparse task type
    def __init__(self, task_file, task_type='xctrack'):
        if task_type == 'xctrack':
            task = xctrack.XCTask(task_file)
        elif task_type == 'pwca':
            # TODO pwca parser
            raise NotImplementedError('{} tasks are not yet supported'.format(task_type))
        else:
            raise NotImplementedError('{} tasks are not yet supported'.format(task_type))

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
        start_passed = False
        goal_distances = {}
        
        for timestamp, point in flight.points.items():

            # race has not started yet
            if timestamp < self.start:
                goal_distances[timestamp] = optimize(point, remaining_turnpoints).distance
                continue

            # race has started, check for start validation
            if start_passed == False:
                goal_distances[timestamp] = optimize(point, remaining_turnpoints).distance

                # this will not work for start without a turnpoint inside !
                if self._close_enough(point, self.sss):
                    start_passed = True
                    del remaining_turnpoints[0]
                    logging.info('START {}, {} wp remaining'.format(timestamp, len(remaining_turnpoints)))

                continue
                
            # at least two turnpoints remaining, check for concentric ones
            if len(remaining_turnpoints) > 1:
                goal_distances[timestamp] = optimize(point, remaining_turnpoints).distance

                if self._close_enough(point, remaining_turnpoints[0]):
                    del remaining_turnpoints[0]
                    logging.info('IN {}, {} wp remaining'.format(timestamp, len(remaining_turnpoints)))

            # only one turnpoint remaining, check for goal
            elif len(remaining_turnpoints) == 1:
                goal_distances[timestamp] = optimize(point, remaining_turnpoints).distance

                if self._close_enough(point, remaining_turnpoints[0]):
                    del remaining_turnpoints[0]
                    logging.info('GOAL {}'.format(timestamp))

            # in goal, fill zeros until landing
            else:
                goal_distances[timestamp] = 0

        if DEBUG ==True:
            self.debug_plot(goal_distances)
            
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


    def debug_plot(self, distances):
        timestamps = [str(x) for x in distances.keys()]
        distances = [float(x) for x in distances.values()]
        plt.plot(distances)
        plt.show()
