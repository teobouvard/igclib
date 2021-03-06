import logging
import os

from aerofiles import openair
from igclib.core import BaseObject
from igclib.core.airspace import Airspace
from igclib.core.flight import Flight
from igclib.geography.elevation import elevation
from igclib.geography.geo import Point
from igclib.optimization.branchbound import compute_score
from rtree.index import Index
from shapely.geometry import LineString
from tqdm import tqdm


class XC(BaseObject):
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        self.points = [Point(p.lat, p.lon, p.altitude) for p in self.flight.to_list()]
        self._bounds = self.get_bounding_box()
        self.score = compute_score(self.flight.to_list())
        self._progress = progress

        ground_altitude = elevation(self.flight.to_list())
        if not ground_altitude:
            self.agl_validable = False
        else:
            for p, altitude in zip(self.points, ground_altitude):
                p.agl = p.z - altitude
            self.agl_validable = True

        self.violations = {}
        if airspace is not None:
            airspace = self.read_airspace(airspace)
            self.validate(airspace)

    def read_airspace(self, airspace):
        index = Index()
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
                            if zone.bounds:
                                index.insert(id(zone), zone.bounds, obj=zone)
                    except KeyError:
                        logging.warning(f'line {reader.reader.lineno} of {os.path.basename(airspace)} - error in previous record')
        return index

    def get_bounding_box(self):
        # TODO this but less stupid
        min_x = min(self.points, key=lambda p: p.x).x
        max_x = max(self.points, key=lambda p: p.x).x
        min_y = min(self.points, key=lambda p: p.y).y
        max_y = max(self.points, key=lambda p: p.y).y
        return min_x, min_y, max_x, max_y

    def serialize(self):
        return {'score': self.score.serialize(), 'violations': self.violations}

    def validate(self, zones):
        # first pass on 2D bounding box
        zones = [inter.object for inter in zones.intersection(self._bounds, objects=True)]
        
        # second pass on altitude bounding box
        max_alt = max(self.points, key=lambda x: x.z).z
        min_alt = min(self.points, key=lambda x: x.z).z
        for i, z in enumerate(zones):
            if (not z.ground_floor) and (z.floor > max_alt):
                del zones[i]
            if (not z.ground_ceiling) and (z.ceiling < min_alt):
                del zones[i]

        # final pass on individual point checking
        for zone in tqdm(zones, desc='checking airspace intersections', disable=self._progress != 'gui'):
            inter = list(filter(zone.__contains__, self.points))
            if inter:
                self.violations[zone.name] = [x.serialize() for x in inter]
