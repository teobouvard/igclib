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
        self.FAI_distance = self.maximize_FAI_triangle()


    def maximize_FAI_triangle(self):
        pass

    
    def save(self, output):
        print(self.FAI_distance)
