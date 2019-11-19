import json
import os
from datetime import datetime, time

from igclib.constants import (PWCA_DETAILS, PWCA_OPEN, PWCA_START, PWCA_STOP, PWCA_TASK,
                              PWCA_TIME_FORMAT, PWCA_TURNPOINT_RADIUS,
                              PWCA_TURNPOINTS, PWCA_TYPE, PWCA_ID, PWCA_TURNPOINT, PWCA_TURNPOINT_NAME, PWCA_TASK_DATE)
from igclib.model.geo import Turnpoint


class PWCATask():

    def __init__(self, task):

        task = task[PWCA_TASK]

        open_time = datetime.strptime(task[PWCA_DETAILS][PWCA_OPEN], PWCA_TIME_FORMAT)
        start_time = datetime.strptime(task[PWCA_DETAILS][PWCA_START], PWCA_TIME_FORMAT)
        stop_time = datetime.strptime(task[PWCA_DETAILS][PWCA_STOP], PWCA_TIME_FORMAT)

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

        self.date = task[PWCA_DETAILS][PWCA_TASK_DATE]
        self.open = time(open_time.hour, open_time.minute, open_time.second)
        self.start = time(start_time.hour, start_time.minute, start_time.second)
        self.stop = time(stop_time.hour, stop_time.minute, stop_time.second)
        self.turnpoints = turnpoints

    @staticmethod
    def _build_wpt(wpt, role='TURNPOINT'):
        return Turnpoint(
            lat=float(wpt[PWCA_TURNPOINT][0]),
            lon=float(wpt[PWCA_TURNPOINT][1]),
            radius=wpt[PWCA_TURNPOINT_RADIUS],
            altitude=0,
            name=wpt[PWCA_TURNPOINT_NAME],
            desc='No description available',
            role=role,
        )
