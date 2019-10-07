import logging
from datetime import datetime, time, timedelta
from parser import xctrack

from constants import distance_computation as distance
from utils.optimizer import optimize

# fast distance computations do not validate waypoints without tolerances
TOLERANCE = 20


class Task():

    optimize 

    def __init__(self, task_file, task_type='xctrack'):
        if task_type == 'xctrack':
            task = xctrack.XCTask(task_file)
        elif task_type == 'pwca':
            # TODO pwca parser
            raise NotImplementedError('{} tasks are not yet supported'.format(task_type))
        else:
            raise NotImplementedError('{} tasks are not yet supported'.format(task_type))

        self.start = task.start
        self.stop = task.stop
        self.takeoff = task.takeoff
        self.sss = task.sss
        self.waypoints = task.waypoints
        self.ess = task.ess
        self.optimized_distance = optimize(self.takeoff, self.waypoints) # to implement

    def timerange(self, start=None, stop=None):
        start = start if start is not None else self.start
        stop = stop if stop is not None else self.stop

        # all this mess is necessary because you can't add datetime.time objects, which are used by aerofiles parser
        current = datetime(1, 1, 1, start.hour, start.minute, start.second)
        stop = datetime(1, 1, 1, stop.hour, stop.minute, stop.second)

        while current < stop:
            yield current.time()
            current += timedelta(seconds=1)

    def validate(self, flight):
        remaining_waypoints = self.waypoints.copy()
        start_passed = False
        remaining_distances = []
        
        for timestamp, point in flight.points.items():

            position = (point['lat'], point['lon'])

            # race has not started yet
            if timestamp < self.start:
                flight.goal_distances[timestamp] = self.optimized_distance
                continue

            # race has started, checking for start validation
            if start_passed == False:
                flight.goal_distances[timestamp] = optimize(point, remaining_waypoints)

                if self.sss['direction'] == 'EXIT' and self.is_in(position, self.sss) or self.sss['direction'] == 'ENTER' and not self.is_in(position, self.sss):
                    start_passed = True
                    del remaining_waypoints[0]

                continue
                
            # at least two turnpoints remaining, check for concentric ones
            if len(remaining_waypoints) > 1:
                flight.goal_distances[timestamp] = optimize(point, remaining_waypoints)
                remaining_distances.append(flight.goal_distances[timestamp])
                if len(remaining_distances) > 1 and remaining_distances[-1]-remaining_distances[-2] > 100:
                    here = True

                if self.is_in(position, remaining_waypoints[0]) and not self.are_concentric(remaining_waypoints[0], remaining_waypoints[1]):
                    del remaining_waypoints[0]
                elif self.are_concentric(remaining_waypoints[0], remaining_waypoints[1]) and not self.is_in(position, remaining_waypoints[0]):
                    del remaining_waypoints[0]

            # only one turnpoint remaining, check for goal
            elif len(remaining_waypoints) == 1:
                flight.goal_distances[timestamp] = optimize(point, remaining_waypoints)

                if self.is_in(position, remaining_waypoints[0]):
                    del remaining_waypoints[0]

            # in goal, fill zeros until landing
            else:
                flight.goal_distances[timestamp] = 0


    def __len__(self):
        return int(self.optimized_distance)

    @staticmethod
    def is_in(pos, wpt):
        return True if distance(pos, (wpt['lat'], wpt['lon'])).meters <= wpt['radius'] + TOLERANCE else False

    @staticmethod
    def are_concentric(wptA, wptB):
        return True if wptA['lat'] == wptB['lat'] and wptA['lon'] == wptB['lon'] else False
