import json
import time as timeparse
from datetime import time

from igclib.constants import (XC_GOAL, XC_GOAL_DEADLINE, XC_SSS, XC_SSS_DIRECTION,
                       XC_SSS_TIMEGATES, XC_TIME_FORMAT, XC_TURNPOINTS,
                       XC_TURNPOINTS_RADIUS, XC_TYPE, XC_WAYPOINT,
                       XC_WAYPOINT_ALT, XC_WAYPOINT_DESC, XC_WAYPOINT_LAT,
                       XC_WAYPOINT_LON, XC_WAYPOINT_NAME)


class XCTask():

    def __init__(self, task_file):
        with open(task_file, 'r') as f:
            task = json.load(f)

        start_time = timeparse.strptime(task[XC_SSS][XC_SSS_TIMEGATES][0], XC_TIME_FORMAT)
        stop_time = timeparse.strptime(task[XC_GOAL][XC_GOAL_DEADLINE], XC_TIME_FORMAT)

        waypoints = []

        for waypoint in task[XC_TURNPOINTS]:

            if waypoint.get(XC_TYPE, None) == 'TAKEOFF':
                self.takeoff = self.wpt_to_dict(waypoint)
                continue
            
            if waypoint.get(XC_TYPE, None) == 'SSS':
                self.sss = self.wpt_to_dict(waypoint)
                self.sss['direction'] = task[XC_SSS][XC_SSS_DIRECTION]

            elif waypoint.get(XC_TYPE, None) == 'ESS':
                self.ess = self.wpt_to_dict(waypoint)

            waypoints.append(self.wpt_to_dict(waypoint))

        self.start = time(start_time.tm_hour, start_time.tm_min, start_time.tm_sec)
        self.stop = time(stop_time.tm_hour, stop_time.tm_min, stop_time.tm_sec)
        self.waypoints = waypoints

    @staticmethod
    def wpt_to_dict(wpt):
        return dict(
            radius=wpt[XC_TURNPOINTS_RADIUS],
            lat=wpt[XC_WAYPOINT][XC_WAYPOINT_LAT],
            lon=wpt[XC_WAYPOINT][XC_WAYPOINT_LON],
            alt=wpt[XC_WAYPOINT][XC_WAYPOINT_ALT],
            name=wpt[XC_WAYPOINT][XC_WAYPOINT_NAME],
            desc=wpt[XC_WAYPOINT][XC_WAYPOINT_DESC],
            type=wpt.get(XC_TYPE, 'TURNPOINT')
        )
