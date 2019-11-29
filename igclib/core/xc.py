from igclib.core.flight import Flight
from geolib import distance
from tqdm import tqdm


class XC():
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        self.FAI_distance = self.maximize_FAI_triangle()


    def maximize_FAI_triangle(self):
        total_distance = 0
        points = list(self.flight.points.values())
        for p1 in tqdm(points):
            for p2 in tqdm(points):
                for p3 in points:
                    dist = sum([
                        distance(p1.lat, p1.lon, p2.lat, p2.lon), 
                        distance(p2.lat, p2.lon, p3.lat, p3.lon),
                        distance(p3.lat, p3.lon, p1.lat, p1.lon)])
                    total_distance = max(total_distance, dist)
        return total_distance

    
    def save(self, output):
        print(self.FAI_distance)
