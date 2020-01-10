# Ondrej Palkovsky - http://www.penguin.cz/~ondrap/algorithm.pdf
from itertools import combinations

from igclib.geography import distance
from sortedcontainers import SortedList  # maybe heapq is a better idea ?


class PointGroup:

    def __init__(self, points):
        self.points = points
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
        return PointGroup(self.points[:middle]), PointGroup(self.points[middle:])

    def __len__(self):
        return len(self.points)

    def __lt__(self, other):
        return distance(*self.bounds) < distance(*other.bounds)

    def __gt__(self, other):
        return distance(*self.bounds) > distance(*other.bounds)

    def __eq__(self, other):
        return distance(*self.bounds) == distance(*other.bounds)


class Candidate:

    def __init__(self, groups):
        self.groups = groups
        self.score = self.max_score()

    def max_score(self):
        max_score = 0
        for v1 in self.groups[0].vertices:
            for v2 in self.groups[1].vertices:
                for v3 in self.groups[2].vertices:
                    dist = distance(v1, v2) + distance(v2, v3) + distance(v3, v1)
                    if dist > max_score:
                        max_score = dist
        return max_score

    def branch(self):
        biggest_group = self.groups.pop(self.groups.index(max(self.groups)))
        group1, group2 = biggest_group.split()
        candidates = Candidate([*self.groups, group1]), Candidate([*self.groups, group2])
        self.groups.append(biggest_group)
        return candidates

    def is_solution(self):
        for g in self.groups:
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
    initial_guess = Candidate([PointGroup(points[i * len(points) // 3:(i + 1) * len(points) // 3]) for i in range(3)])
    candidates = SortedList([initial_guess])

    while not candidates[-1].is_solution():
        new_candidates = candidates[-1].branch()
        del candidates[-1]
        for c in new_candidates:
            candidates.add(c)

    return candidates[-1]
