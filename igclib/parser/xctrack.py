import json
import time as timeparse
from datetime import time

from constants import (XC_GOAL, XC_GOAL_DEADLINE, XC_SSS, XC_SSS_TIMEGATES,
                       XC_TIME_FORMAT, XC_TURNPOINTS, XC_TURNPOINTS_RADIUS,
                       XC_WAYPOINT, XC_WAYPOINT_ALT, XC_WAYPOINT_DESC,
                       XC_WAYPOINT_LAT, XC_WAYPOINT_LON, XC_WAYPOINT_NAME, XC_TYPE)


class XCTask():

    def __init__(self, task_file):
        with open(task_file, 'r') as f:
            task = json.load(f)

        start_time = timeparse.strptime(task[XC_SSS][XC_SSS_TIMEGATES][0], XC_TIME_FORMAT)
        stop_time = timeparse.strptime(task[XC_GOAL][XC_GOAL_DEADLINE], XC_TIME_FORMAT)

        waypoints = []
        for waypoint in task[XC_TURNPOINTS]:
            waypoints.append(dict(
                radius=waypoint[XC_TURNPOINTS_RADIUS],
                lat=waypoint[XC_WAYPOINT][XC_WAYPOINT_LAT],
                lon=waypoint[XC_WAYPOINT][XC_WAYPOINT_LON],
                alt=waypoint[XC_WAYPOINT][XC_WAYPOINT_ALT],
                name=waypoint[XC_WAYPOINT][XC_WAYPOINT_NAME],
                desc=waypoint[XC_WAYPOINT][XC_WAYPOINT_DESC],
                type=waypoint.get(XC_TYPE, 'TURNPOINT'),
            ))
        

        self.start = time(start_time.tm_hour, start_time.tm_min, start_time.tm_sec)
        self.stop = time(stop_time.tm_hour, stop_time.tm_min, stop_time.tm_sec)
        self.waypoints = waypoints
