import json
import time as timeparse
from datetime import time

from utils.optimizer import Optimizer

from constants import XC_TIME_FORMAT
from constants import XC_SSS, XC_SSS_TIMEGATES
from constants import XC_GOAL, XC_GOAL_DEADLINE

class XCTask():

    def __init__(self, task_file):
        with open(task_file, 'r') as f:
            task = json.load(f)

        start_time = timeparse.strptime(task[XC_SSS][XC_SSS_TIMEGATES][0], XC_TIME_FORMAT)
        stop_time = timeparse.strptime(task[XC_GOAL][XC_GOAL_DEADLINE], XC_TIME_FORMAT)

        self.start = time(start_time.tm_hour, start_time.tm_min, start_time.tm_sec)
        self.stop = time(stop_time.tm_hour, stop_time.tm_min, stop_time.tm_sec)