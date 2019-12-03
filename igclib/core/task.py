import base64
import json
import logging
import os

from igclib.core import BaseObject
from igclib.geography import distance, heading
from igclib.geography.optimizer import optimize
from igclib.parsers import taskparse
from igclib.time.timeop import next_second


class Task(BaseObject):
    """
    Creates a Task object. The way this is done is really bad, and any help would be appreciated. As of now, this class checks if the input task (file or b64) "fits" in each parser implemented.
    When a parser does not raise a KeyError, the task is assumed to be of this format and its attributes are copied back to the Task object. I feel that there is a smarter way to do this, probably with inheritance.
    However, task format is not known in advance so trying each format seems like the easiest thing to do.

    Args:
        task (str): Path to or base64 representation of a task file.
    Raises:
        NotImplementedError: If the task could not be parsed.
    """

    def __init__(self, task):

        # try to base64 decode the task
        if not os.path.isfile(task):
            try:
                task = base64.b64decode(task)
                task = json.loads(task)
            except TypeError:
                logging.debug(f'Task is not base64')

        else:
            with open(task, 'r') as f:
                task = json.load(f)

        # try to parse with every implemented format, raise if no match
        for task_format in [taskparse.XCTask, taskparse.PWCATask, taskparse.RawTask, taskparse.IGCLIBTask]:
            try:
                task = task_format(task)
                break
            except (KeyError, TypeError):
                logging.debug(f'Task format does not fit into {task_format}')

        if not hasattr(task, 'takeoff'):
            raise NotImplementedError('Task format not recognized')

        self.__dict__.update(task.__dict__)

        # if the goal is a line, we need a to compute its validation with the following technique
        # we compute the heading between the goal and the first previous turnpoint which has a different center
        # during validation, we compute the heading between the pilot and the goal center
        # when the absolute difference between these two headings is greater than 90~ish° (and is inside the goal radius), the goal is validated
        # not only does this allow us to validate goal line, but it also helps drawing goal lines in TaskCreator by directly having the line normal direction
        if self.goal_style == 'LINE':
            index_last_turnpoint = -2
            while distance(self.turnpoints[index_last_turnpoint], self.turnpoints[-1]) < 1:
                index_last_turnpoint -= 1
            self.last_leg_heading = heading(self.turnpoints[index_last_turnpoint], self.turnpoints[-1])

        self.opti = optimize(self.takeoff, self.turnpoints)

    def _timerange(self, start=None, stop=None):
        current = start or self.open
        stop = stop or self.stop
        while current < stop:
            yield current
            current = next_second(current)

    def update_tag_times(self, times):
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
                optimizer_init_vector = opti._angles

            # race has started, check next turnpoint's closeness and validate it
            elif remaining_turnpoints:
                opti = optimize(point, remaining_turnpoints, prev_opti=optimizer_init_vector)
                goal_distances[timestamp] = opti.distance
                optimizer_init_vector = opti._angles

                # if only one turnpoint left, validate it as goal line by heading difference (95° to be sure the goal line is behind)
                if len(remaining_turnpoints) == 1:
                    goal_heading = heading(point, remaining_turnpoints[-1])
                    delta_heading = abs(self.last_leg_heading - goal_heading)
                    if delta_heading > 95:
                        tag_times.append(timestamp)
                        del remaining_turnpoints[0]
                        logging.debug(f'{flight.pilot_id} passed TP at {timestamp}, {len(remaining_turnpoints)} wp remaining')

                elif point.close_enough(remaining_turnpoints[0]):
                    tag_times.append(timestamp)
                    del remaining_turnpoints[0]
                    logging.debug(f'{flight.pilot_id} passed TP at {timestamp}, {len(remaining_turnpoints)} wp remaining')

            # in goal, fill with zeros until landing
            else:
                goal_distances[timestamp] = 0

        return flight.pilot_id, goal_distances, tag_times

    def __len__(self):
        return int(self.opti.distance)
