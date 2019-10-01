import logging
from datetime import datetime, time, timedelta

from igclib.parser import xctrack

class Task():

    def __init__(self, task_file):
        task = xctrack.XCTask(task_file).read()

        self.start = time(12,0,0)
        self.stop = time(19,0,0)

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