# Algorithm designed by Ondrej Palkovsky - http://www.penguin.cz/~ondrap/algorithm.pdf
from itertools import combinations

from igclib.core import BaseObject
from igclib.geography import distance
from sortedcontainers import SortedList  # maybe heapq is a better idea ?


class PointGroup(BaseObject):

    def __init__(self, points):
        self.points = list(points)
        self.bounds = self.bounding_box()
        self.vertices = self.get_vertices()

    def bounding_box(self):
        lats = [_.lat for _ in self.points]
        lons = [_.lon for _ in self.points]
        return min(lats), min(lons), max(lats), max(lons)

    def get_vertices(self):
        return ((self.bounds[0], self.bounds[1]), (self.bounds[0], self.bounds[3]), (self.bounds[2], self.bounds[1]), (self.bounds[2], self.bounds[3]))

    def split(self):
        middle = len(self) // 2
        first_half = self.points[:middle]
        last_half = self.points[middle:]
        return PointGroup(first_half), PointGroup(last_half)

    def __len__(self):
        return len(self.points)

    def __lt__(self, other):
        return distance(*self.bounds) < distance(*other.bounds)

    def __gt__(self, other):
        return distance(*self.bounds) > distance(*other.bounds)

    def __eq__(self, other):
        return distance(*self.bounds) == distance(*other.bounds)


class Candidate(BaseObject):

    def __init__(self, groups, before=None, after=None, closed=False):
        self._groups = groups
        self._before = [self._groups[0].points[0]] if before is None else before
        self._after = [self._groups[-1].points[-1]] if after is None else after
        self._closed = closed
        self.points, self.distance, self.xc_type, self.score = self.max_score()

    def max_score(self):
        xc_score = 0
        xc_distance = 0
        xc_type = None
        xc_points = []

        for v1 in self._groups[0].vertices:
            for v2 in self._groups[1].vertices:
                for v3 in self._groups[2].vertices:
                    legs = [distance(v1, v2), distance(v2, v3), distance(v3, v1)]
                    dist = sum(legs)
                    if self.is_closed(tol=0.05 * dist):
                        if min(legs) / dist > 0.28:  # TODO check coefficient ?
                            current_score = 0.0014 * dist
                            current_type = 'FAI triangle'
                        else:
                            current_score = 0.0012 * dist
                            current_type = 'flat triangle'
                    else:
                        current_score = 0.001 * dist
                        current_type = '3 points'

                    if current_score > xc_score:
                        xc_score = current_score
                        xc_type = current_type
                        xc_distance = dist
                        xc_points = [v1, v2, v3]

        return xc_points, xc_distance, xc_type, xc_score

    def is_closed(self, tol=2000):
        if self._closed:
            return True
        for p1 in self._before:
            for p2 in self._after:
                if distance(p1, p2) < tol:
                    self._closed = True
                    return True
        return False

    def branch(self):
        index_biggest_group = self._groups.index(max(self._groups))
        biggest_group = self._groups.pop(index_biggest_group)
        group1, group2 = biggest_group.split()
        if (index_biggest_group == 0) or (index_biggest_group == 2):
            new_before = self._before.copy()
            new_before.extend(group1.points)
            new_after = self._after.copy()
            new_after.extend(group2.points)
        else:
            new_before = self._before
            new_after = self._after
        candidates = Candidate([*self._groups, group1], after=new_after, closed=self._closed), Candidate([*self._groups, group2], before=new_before, closed=self._closed)
        self._groups.append(biggest_group)
        return candidates

    def is_solution(self):
        for g in self._groups:
            if len(g) > 1:
                return False
        return True

    def __lt__(self, other):
        return self.score < other.score

    def __gt__(self, other):
        return self.score > other.score

    def __eq__(self, other):
        return self.score == other.score


def compute_score(points):
    initial_guess = Candidate([PointGroup(points[i * len(points) // 3:(i + 1) * len(points) // 3]) for i in range(3)], None)
    candidates = SortedList([initial_guess])

    while not candidates[-1].is_solution():
        new_candidates = candidates[-1].branch()
        del candidates[-1]
        for c in new_candidates:
            candidates.add(c)

    return candidates[-1]
