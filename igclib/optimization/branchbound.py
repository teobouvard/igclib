# Ondrej Palkovsky - http://www.penguin.cz/~ondrap/algorithm.pdf
from itertools import combinations

from igclib.geography import distance
from sortedcontainers import SortedList


class PointGroup:

    def __init__(self, points):
        self.points = points
        self.bounds = self.bounding_box()

    def bounding_box(self):
        lats = [_.lat for _ in self.points]
        lons = [_.lon for _ in self.points]
        return min(lats), min(lons), max(lats), max(lons)

    def split(self):
        middle = len(self) // 2
        return PointGroup(self.points[:middle]), PointGroup(self.points[middle:])

    def __len__(self):
        return len(self.points)

    def __lt__(self, other):
        return distance(self.bounds) < distance(other.bounds)

    def __gt__(self, other):
        return distance(self.bounds) > distance(other.bounds)

    def __eq__(self, other):
        return distance(self.bounds) == distance(other.bounds)


class Candidate:

    def __init__(self, groups):
        self.groups = groups
        self.to_split = None
        self.score = self.score()

    def score(self):
        # TODO group distance + triangle close
        pass

    def branch(self):
        pass

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

    while not candidates[0].is_solution():
        candidates.extend(candidates[0].branch())
