import logging
from datetime import datetime, time, timedelta
from parser import xctrack

from constants import XC_SSS_TIMEGATES
from utils.optimizer import Optimizer


class Task():

    def __init__(self, task_file, task_type='xctrack'):
        if task_type == 'xctrack':
            task = xctrack.XCTask(task_file)
        elif task_type == 'pwca':
            # TODO pwca parser
            raise NotImplementedError('{} tasks are not yet supported'.format(task_type))
        else:
            raise NotImplementedError('{} tasks are not yet supported'.format(task_type))

        #self.start = task.start
        #self.stop = task.stop
        self.start = time(12,0,0)
        self.stop = time(20,0,0)
        self.waypoints = task.waypoints

    def timerange(self, start=None, stop=None):
        start = start if start is not None else self.start
        stop = stop if stop is not None else self.stop

        # all this mess is necessary because you can't add datetime.time objects, which are used by aerofiles parser
        current = datetime(1, 1, 1, start.hour, start.minute, start.second)
        stop = datetime(1, 1, 1, stop.hour, stop.minute, stop.second)

        while current < stop:
            yield current.time()
            current += timedelta(seconds=1)

    def __len__(self):
        return 0 #NotImplemented
