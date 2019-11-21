import json
import os
from datetime import datetime, time

from igclib.constants import (IGCLIB_ESS, IGCLIB_GOAL, IGCLIB_SSS,
                              IGCLIB_TAKEOFF, IGCLIB_TURNPOINT_ALT,
                              IGCLIB_TURNPOINT_ROLE, IGCLIB_TURNPOINTS)
from igclib.model.geo import Turnpoint


class IGCLIBTask():

    def __init__(self, task):

        open_time = datetime.strptime(task[PWCA_DETAILS][PWCA_OPEN], PWCA_TIME_FORMAT)
        start_time = datetime.strptime(task[PWCA_DETAILS][PWCA_START], PWCA_TIME_FORMAT)
        stop_time = datetime.strptime(task[PWCA_DETAILS][PWCA_STOP], PWCA_TIME_FORMAT)

        self.takeoff = self.build_wpt(task[IGCLIB_TAKEOFF])
        self.sss = self.build_wpt(task[IGCLIB_SSS])
        self.ess = self.build_wpt(task[IGCLIB_ESS])

        self.turnpoints = []
        for waypoint in task[IGCLIB_TURNPOINTS]:
            self.turnpoints.append(self.build_wpt(waypoint))

        self.date = task.get(IGCLIB_DATE, None)
        self.open = time(open_time.hour, open_time.minute, open_time.second)
        self.start = time(start_time.hour, start_time.minute, start_time.second)
        self.stop = time(stop_time.hour, stop_time.minute, stop_time.second)


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
