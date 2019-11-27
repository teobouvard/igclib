import json
import os
from datetime import datetime, time

from igclib.constants import (IGCLIB_ESS, IGCLIB_GOAL, IGCLIB_SSS, IGCLIB_TAKEOFF, IGCLIB_TURNPOINT_ALT, IGCLIB_TURNPOINT_LAT, IGCLIB_TURNPOINT_LON, IGCLIB_TURNPOINT_RADIUS, IGCLIB_TURNPOINT_ROLE, IGCLIB_TURNPOINTS, PWCA_DETAILS, PWCA_ID, PWCA_OPEN, PWCA_START, PWCA_STOP, PWCA_TASK, PWCA_TASK_DATE,
                              PWCA_TIME_FORMAT, PWCA_TURNPOINT, PWCA_TURNPOINT_NAME, PWCA_TURNPOINT_RADIUS, PWCA_TURNPOINTS, PWCA_TYPE, XC_GOAL, XC_GOAL_DEADLINE, XC_SSS, XC_SSS_TIMEGATES, XC_TIME_FORMAT, XC_TURNPOINTS, XC_TURNPOINTS_RADIUS, XC_TYPE, XC_WAYPOINT, XC_WAYPOINT_ALT, XC_WAYPOINT_DESC,
                              XC_WAYPOINT_LAT, XC_WAYPOINT_LON, XC_WAYPOINT_NAME)
from igclib.geography.geo import Turnpoint
from igclib.time.timeop import add_offset


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

        self.date = task[PWCA_DETAILS][PWCA_TASK_DATE].strip()
        self.open = time(open_time.hour, open_time.minute, open_time.second)
        self.start = time(start_time.hour, start_time.minute, start_time.second)
        self.stop = time(stop_time.hour, stop_time.minute, stop_time.second)
        self.turnpoints = turnpoints
        self.goal_style = 'LINE'

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


class XCTask():

    def __init__(self, task):
        start_time = datetime.strptime(task[XC_SSS][XC_SSS_TIMEGATES][0], XC_TIME_FORMAT)
        stop_time = datetime.strptime(task[XC_GOAL][XC_GOAL_DEADLINE], XC_TIME_FORMAT)

        turnpoints = []
        for waypoint in task[XC_TURNPOINTS]:
            if waypoint.get(XC_TYPE, None) == 'TAKEOFF':
                self.takeoff = self._build_wpt(waypoint)
                continue
            elif waypoint.get(XC_TYPE, None) == 'SSS':
                self.sss = self._build_wpt(waypoint, task)
            elif waypoint.get(XC_TYPE, None) == 'ESS':
                self.ess = self._build_wpt(waypoint)
            turnpoints.append(self._build_wpt(waypoint))

        self.date = 'Unknown'
        self.open = add_offset(time(start_time.hour, start_time.minute, start_time.second), hours=-1)
        self.start = time(start_time.hour, start_time.minute, start_time.second)
        self.stop = time(stop_time.hour, stop_time.minute, stop_time.second)
        self.turnpoints = turnpoints
        self.goal_style = task[XC_GOAL][XC_TYPE]

    @staticmethod
    def _build_wpt(wpt, task=None):
        return Turnpoint(
            lat=wpt[XC_WAYPOINT][XC_WAYPOINT_LAT],
            lon=wpt[XC_WAYPOINT][XC_WAYPOINT_LON],
            radius=wpt[XC_TURNPOINTS_RADIUS],
            altitude=wpt[XC_WAYPOINT][XC_WAYPOINT_ALT],
            name=wpt[XC_WAYPOINT][XC_WAYPOINT_NAME],
            desc=wpt[XC_WAYPOINT][XC_WAYPOINT_DESC],
            role=wpt.get(XC_TYPE, 'TURNPOINT'),
        )


class IGCLIBTask():

    def __init__(self, task):
        #open_time = datetime.strptime(task[PWCA_DETAILS][PWCA_OPEN], PWCA_TIME_FORMAT)
        #start_time = datetime.strptime(task[PWCA_DETAILS][PWCA_START], PWCA_TIME_FORMAT)
        #stop_time = datetime.strptime(task[PWCA_DETAILS][PWCA_STOP], PWCA_TIME_FORMAT)

        self.takeoff = self.build_wpt(task[IGCLIB_TAKEOFF])
        self.sss = self.build_wpt(task[IGCLIB_SSS])
        self.ess = self.build_wpt(task[IGCLIB_ESS])

        self.turnpoints = []
        for waypoint in task[IGCLIB_TURNPOINTS]:
            self.turnpoints.append(self.build_wpt(waypoint))

        self.date = task.get(IGCLIB_DATE, None).strip()
        self.open = time(open_time.hour, open_time.minute, open_time.second)
        self.start = time(start_time.hour, start_time.minute, start_time.second)
        self.stop = time(stop_time.hour, stop_time.minute, stop_time.second)
        self.goal_style = 'LINE'

    @staticmethod
    def build_wpt(wpt):
        return Turnpoint(
            lat=wpt[IGCLIB_TURNPOINT_LAT],
            lon=wpt[IGCLIB_TURNPOINT_LON],
            radius=wpt[IGCLIB_TURNPOINT_RADIUS],
            altitude=wpt[IGCLIB_TURNPOINT_ALT],
            name=wpt[IGCLIB_TURNPOINT_NAME],
            desc=wpt[IGCLIB_TURNPOINT_DESC],
            role=wpt[IGCLIB_TURNPOINT_ROLE],
        )


class RawTask():

    def __init__(self, task):
        self.turnpoints = []
        for waypoint in task:
            self.turnpoints.append(self.build_wpt(waypoint))

        self.takeoff = self.turnpoints.pop(0)
        self.goal_style = 'LINE'

    @staticmethod
    def build_wpt(wpt):
        return Turnpoint(
            lat=float(wpt[IGCLIB_TURNPOINT_LAT]),
            lon=float(wpt[IGCLIB_TURNPOINT_LON]),
            radius=float(wpt[IGCLIB_TURNPOINT_RADIUS]),
        )
