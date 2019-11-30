import logging
import os

from aerofiles import openair
from igclib.core.flight import Flight
from igclib.geography.optimizer import maximize_distance
from tqdm import tqdm
from igclib.core.base import BaseObject

from geolib import distance


class XC(BaseObject):
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        #self.triangle_distance = maximize_distance(self.flight)
        if airspace is not None:
            self.airspace = self.parse_airspace(airspace)
        else:
            self.airspace = None

    def parse_airspace(self, airspace):
        records = []
        with open(airspace, 'r') as f:
            reader = openair.Reader(f)
            for record, error in reader:
                if error:
                    logging.warning(f'line {error.lineno} of {os.path.basename(airspace)} - {error}')
                records.append(record)

        return records
