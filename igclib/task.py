from datetime import time, datetime, timedelta

class Task():

    def __init__(self, task_file):
        self.start = time(14,0,0)
        self.stop = time(16,0,0)

    def timerange(self, start=None, stop=None):
        start = start if start is not None else self.start
        stop = stop if stop is not None else self.stop

        current = datetime(1, 1, 1, start.hour, start.minute, start.second)
        stop = datetime(1, 1, 1, stop.hour, stop.minute, stop.second)

        while current < stop:
            yield current.time()
            current += timedelta(seconds=1)