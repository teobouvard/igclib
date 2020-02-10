import logging

from igclib.geography import destination
from igclib.geography.converters import parse_altitude
from igclib.geography.geo import Arc
from shapely.geometry import Polygon

NORTH = 0
SOUTH = 180
EAST = 90
WEST = -90


class Airspace:

    def __init__(self, record):
        self.name = record.get('name')
        self.airspace_class = record.get('class')
        self.floor, self.ground_floor = parse_altitude(record.get('floor'))
        self.ceiling, self.ground_ceiling = parse_altitude(record.get('ceiling'))
        assert self.floor < self.ceiling
        self.polygon, self.arcs = self.build(record.get('elements'))
        self.bounds = self.compute_bounds()

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

    def compute_bounds(self):
        bounds = None
        if self.polygon:
            bounds = list(self.polygon.bounds)
        if self.arcs:
            north_points = []
            south_points = []
            east_points = []
            west_points = []
            for arc in self.arcs:
                north_points.append(destination(arc, arc.radius, NORTH)[0])
                south_points.append(destination(arc, arc.radius, SOUTH)[0])
                east_points.append(destination(arc, arc.radius, EAST)[1])
                west_points.append(destination(arc, arc.radius, WEST)[1])
            if bounds:
                bounds[0] = min(bounds[0], min(south_points))
                bounds[1] = min(bounds[1], min(west_points))
                bounds[2] = max(bounds[2], max(north_points))
                bounds[3] = max(bounds[0], max(east_points))
            else:
                bounds = min(south_points), min(west_points), max(north_points), max(east_points)
        return bounds
