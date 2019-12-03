import logging

from igclib.geography.converters import parse_altitude
from igclib.geography.geo import Arc
from shapely.geometry import Polygon


class Airspace:

    def __init__(self, record):
        self.name = record.get('name')
        self.floor, self.ground_floor = parse_altitude(record.get('floor'))
        self.ceiling, self.ground_ceiling = parse_altitude(record.get('ceiling'))
        self.polygon, self.arcs = self.build(record.get('elements'))
        self.airspace_class = record.get('class')

    def __contains__(self, point):
        if self.ground_floor and point.agl < self.floor:
            return False
        if self.ground_ceiling and point.agl > self.ceiling:
            return False
        if not self.ground_floor and point.z < self.floor:
            return False
        if not self.ground_ceiling and point.z > self.ceiling:
            return False
        if self.polygon and self.polygon.contains(point):
            return True
        if self.arcs:
            for arc in self.arcs:
                if point in arc:
                    return True
        return False

    def build(self, elements):
        points = []
        arcs = []
        for e in elements:
            if e['type'] == 'point':
                points.append(e['location'])
            elif e['type'] == 'arc':
                arcs.append(Arc(*e['center'], p1=e['start'], p2=e['end']))
                points.extend([e['start'], e['end']])
            elif e['type'] == 'circle':
                arcs.append(Arc(*e['center'], radius=e['radius']))

        if not points:
            return None, arcs
        if len(points) < 3:
            logging.warning(f'{self.name} does not contain enough points to build a polygon')
            return None, arcs
        return Polygon(points), arcs
