import json
import os
import time as timeparse
from datetime import time

from igclib.constants import (PWCA_DETAILS, PWCA_START, PWCA_STOP, PWCA_TASK,
                              PWCA_TIME_FORMAT, PWCA_TURNPOINT_RADIUS,
                              PWCA_TURNPOINTS, PWCA_TYPE, PWCA_ID, PWCA_TURNPOINT, PWCA_TURNPOINT_NAME)
from igclib.model.geo import Turnpoint


class PWCATask():

    def __init__(self, task_file):

        if os.path.isfile(task_file):
            with open(task_file, 'r') as f:
                task = json.load(f)[PWCA_TASK]
        else:
            task = json.loads(task_file)[PWCA_TASK]

        start_time = timeparse.strptime(task[PWCA_DETAILS][PWCA_START], PWCA_TIME_FORMAT)
        stop_time = timeparse.strptime(task[PWCA_DETAILS][PWCA_STOP], PWCA_TIME_FORMAT)

        turnpoints = []

        for waypoint in task[PWCA_TURNPOINTS]:

            if waypoint.get(PWCA_ID, None) == 'TO':
                self.takeoff = self._build_wpt(waypoint, role='TAKEOFF')
                continue
            
            elif waypoint.get(PWCA_TYPE, None) == 'SS':
                self.sss = self._build_wpt(waypoint, role='SSS')

            elif waypoint.get(PWCA_TYPE, None) == 'ES':
                self.ess = self._build_wpt(waypoint, role='ESS')

            turnpoints.append(self._build_wpt(waypoint))

        self.start = time(start_time.tm_hour, start_time.tm_min, start_time.tm_sec)
        self.stop = time(stop_time.tm_hour, stop_time.tm_min, stop_time.tm_sec)
        self.turnpoints = turnpoints

    @staticmethod
    def _build_wpt(wpt, role='TURNPOINT'):
        return Turnpoint(
            lat=float(wpt[PWCA_TURNPOINT][0]),
            lon=float(wpt[PWCA_TURNPOINT][1]),
            radius=wpt[PWCA_TURNPOINT_RADIUS],
            altitude=0,
            name=wpt[PWCA_TURNPOINT_NAME],
            desc='',
            role=role,
        )
