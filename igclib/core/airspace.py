import logging

from igclib.geography.converters import parse_altitude
from igclib.geography.geo import Arc
from shapely.geometry import Point, Polygon


class Airspace:

    def __init__(self, record):
        self.name = record.get('name')
        self.floor = parse_altitude(record.get('floor'))
        self.ceiling = parse_altitude(record.get('ceiling'))
        self.polygon, self.arcs = self.build_poly(record.get('elements'))
        self.airspace_class = record.get('class')

    def get_bounding_box(self):
        pass

    def __contains__(self, point):
        if point.z > self.ceiling or point.z < self.floor:
            return False
        if self.polygon and self.polygon.contains(point):
            return True
        if self.arcs:
            for arc in self.arcs:
                if point in arc:
                    return True
        return False

    def build_poly(self, elements):
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
        elif len(points) < 3:
            logging.warn(f'{self.name} does not contain enough points to build a polygon')
            return None, arcs
        else:
            return Polygon(points), arcs
