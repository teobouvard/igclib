import json
import time as timeparse
from datetime import time
import os

from igclib.model.geo import Turnpoint
from igclib.constants import (XC_GOAL, XC_GOAL_DEADLINE, XC_SSS, XC_SSS_DIRECTION,
                       XC_SSS_TIMEGATES, XC_TIME_FORMAT, XC_TURNPOINTS,
                       XC_TURNPOINTS_RADIUS, XC_TYPE, XC_WAYPOINT,
                       XC_WAYPOINT_ALT, XC_WAYPOINT_DESC, XC_WAYPOINT_LAT,
                       XC_WAYPOINT_LON, XC_WAYPOINT_NAME)
                       


class XCTask():

    def __init__(self, task_file):
        
        if os.path.isfile(task_file):
            with open(task_file, 'r') as f:
                task = json.load(f)
        else:
            task = json.loads(task_file)

        start_time = timeparse.strptime(task[XC_SSS][XC_SSS_TIMEGATES][0], XC_TIME_FORMAT)
        stop_time = timeparse.strptime(task[XC_GOAL][XC_GOAL_DEADLINE], XC_TIME_FORMAT)

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
        self.start = time(start_time.tm_hour, start_time.tm_min, start_time.tm_sec)
        self.stop = time(stop_time.tm_hour, stop_time.tm_min, stop_time.tm_sec)
        self.turnpoints = turnpoints

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
            direction=task[XC_SSS][XC_SSS_DIRECTION] if task is not None else None
        )
