# Algorithm designed by Ondrej Palkovsky - http://www.penguin.cz/~ondrap/algorithm.pdf
from itertools import combinations

from igclib.geography import distance
from sortedcontainers import SortedList  # maybe heapq is a better idea ?


class PointGroup:

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


class Candidate:

    def __init__(self, groups, before=None, after=None):
        self.groups = groups
        self.before = [self.groups[0].points[0]] if before is None else before
        self.after = [self.groups[-1].points[-1]] if after is None else after
        self.score, self.xc_type = self.max_score()

    def max_score(self):
        max_score = 0
        xc_type = None
        for v1 in self.groups[0].vertices:
            for v2 in self.groups[1].vertices:
                for v3 in self.groups[2].vertices:
                    dist = distance(v1, v2) + distance(v2, v3) + distance(v3, v1)
                    if self.is_closed(tol=0.05 * dist):
                        current_score = 0.0014 * dist
                        current_type = 'FAI'
                    else:
                        current_score = 0.001*dist
                        current_type = '3-points'

                    if current_score > max_score:
                        max_score = current_score
                        xc_type = current_type
        return max_score, xc_type

    def is_closed(self, tol=2000):
        min_distance = distance(self.before[0], self.after[-1])
        for p1 in self.before:
            for p2 in self.after:
                min_distance = min(min_distance, distance(p1, p2))
        return min_distance < tol

    def branch(self):
        index_biggest_group = self.groups.index(max(self.groups))
        biggest_group = self.groups.pop(index_biggest_group)
        group1, group2 = biggest_group.split()
        if (index_biggest_group == 0) or (index_biggest_group == 2):
            new_before = self.before.copy()
            new_before.extend(group1.points)
            new_after = self.after.copy()
            new_after.extend(group2.points)
        else:
            new_before = self.before
            new_after = self.after
        candidates = Candidate([*self.groups, group1], after=new_after), Candidate([*self.groups, group2], before=new_before)
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
    initial_guess = Candidate([PointGroup(points[i * len(points) // 3:(i + 1) * len(points) // 3]) for i in range(3)], None)
    candidates = SortedList([initial_guess])

    while not candidates[-1].is_solution():
        new_candidates = candidates[-1].branch()
        del candidates[-1]
        for c in new_candidates:
            candidates.add(c)

    return candidates[-1]
