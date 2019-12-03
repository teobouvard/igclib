import logging
import multiprocessing
multiprocessing.set_start_method('spawn', True)
import os

from aerofiles import openair
from igclib.core import BaseObject
from igclib.core.airspace import Airspace
from igclib.core.flight import Flight
from igclib.geography.elevation import elevation
from igclib.geography.geo import Point
from tqdm import tqdm
from collections import defaultdict


class XC(BaseObject):
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        self.points = [Point(p.lat, p.lon, p.altitude) for p in self.flight.to_list()]
        ground_altitude = elevation(self.flight.to_list())
        if not ground_altitude:
            self.agl_validable = False
        else:
            for p, altitude in zip(self.points, ground_altitude):
                p.agl = p.z - altitude
            self.agl_validable = True

        if airspace is not None:
            airspace = self.read_airspace(airspace)
            self.violations = self.validate(airspace)

    def read_airspace(self, airspace):
        zones = []
        with open(airspace, 'r') as f:
            reader = openair.Reader(f)
            for record, error in reader:
                if error:
                    logging.warning(f'line {error.lineno} of {os.path.basename(airspace)} - {error}')
                else:
                    try:
                        zone = Airspace(record)
                        if not self.agl_validable and (zone.ground_floor or zone.ground_ceiling):
                            logging.warning(f'{zone.name} will not be checked because ground altitude of flight could not be retrieved.')
                        else:
                            zones.append(zone)
                    except KeyError:
                        logging.warning(f'line {reader.reader.lineno} of {os.path.basename(airspace)} - error in previous record')
        return zones

    #def validate(self, zones):
    #    violations = {}
    #    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
    #        for zone, inter in tqdm(p.imap_unordered(self.check_intersections, zones, chunksize=int(len(zones)/multiprocessing.cpu_count())), total=len(zones), desc='checking airspace intersections'):
    #            if inter:
    #                violations[zone.name] = inter
    #    return violations

    def validate(self, zones):
        violations = defaultdict(list)
        for zone in tqdm(zones, desc='checking airspace intersections'):
            for point in self.points:
                if point in zone:
                    violations[zone.name].append(point)
        return violations

    def check_intersections(self, zone):
        return zone, [p.x for p in self.points if p in zone]

    def serialize(self):
        return {'violations': self.violations}
