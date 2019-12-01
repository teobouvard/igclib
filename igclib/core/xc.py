import logging
import os

from aerofiles import openair
from igclib.core import BaseObject
from igclib.core.airspace import Airspace
from igclib.core.flight import Flight
from igclib.geography import distance
from igclib.geography.optimizer import maximize_distance
from tqdm import tqdm
from shapely.geometry import LineString, Point


class XC(BaseObject):
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        if airspace is not None:
            airspace = self.parse_airspace(airspace)
            points = [Point(p.lat, p.lon, p.altitude) for p in self.flight]
            self.intersections = self.validate(airspace, points)
            print(len(self.intersections))

    def parse_airspace(self, airspace):
        if airspace is None:
            return None
        zones = []
        with open(airspace, 'r') as f:
            reader = openair.Reader(f)
            for record, error in reader:
                if error:
                    logging.warning(f'line {error.lineno} of {os.path.basename(airspace)} - {error}')
                else:
                    try:
                        zones.append(Airspace(record))
                    except KeyError:
                        logging.warning(f'line {reader.reader.lineno} of {os.path.basename(airspace)} - error in previous record')
        return zones

    def validate(self, zones, points):
        intersections = []
        for zone in tqdm(zones):
            for point in points:
                if point in zone:
                    intersections.append(point)
        return intersections
