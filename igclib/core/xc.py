import logging
import os

from aerofiles import openair
from igclib.core.flight import Flight
from igclib.geography.optimizer import maximize_distance
from tqdm import tqdm
from igclib.core.base import BaseObject
from igclib.core.airspace import Airspace

from geolib import distance


class XC(BaseObject):
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        #self.triangle_distance = maximize_distance(self.flight)
        self.airspace = self.parse_airspace(airspace)

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
