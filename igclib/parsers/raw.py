import json
import os
from datetime import datetime, time

from igclib.constants import IGCLIB_TURNPOINT_LAT, IGCLIB_TURNPOINT_LON, IGCLIB_TURNPOINT_RADIUS
from igclib.model.geo import Turnpoint


class RawTask():

    def __init__(self, task):
        self.turnpoints = []
        for waypoint in task:
            self.turnpoints.append(self.build_wpt(waypoint))

        self.takeoff = self.turnpoints.pop(0)

    @staticmethod
    def build_wpt(wpt):
        return Turnpoint(
            lat=float(wpt[IGCLIB_TURNPOINT_LAT]),
            lon=float(wpt[IGCLIB_TURNPOINT_LON]),
            radius=float(wpt[IGCLIB_TURNPOINT_RADIUS]),
        )
