from igclib.core.flight import Flight
from geolib import distance
from tqdm import tqdm
from igclib.geography.optimizer import maximize_distance


class XC():
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        self.triangle_distance = maximize_triangle()

    def save(self, output):
        print(self.triangle_distance)
