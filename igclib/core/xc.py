from igclib.core.flight import Flight
from geolib import distance
from tqdm import tqdm
from igclib.geography.optimizer import maximize_distance
from aerofiles import openair 


class XC():
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        #self.triangle_distance = maximize_distance(self.flight)
        if airspace is not None:
            self.airspace = self.parse_airspace(airspace)
        else: 
            self.airspace = None

        print(self.airspace)

    
    def parse_airspace(self, airspace):
        records = []
        errors = []
        with open(airspace, 'r') as f:
            reader = openair.Reader(f)
            for record, error in reader:
                if error:
                    errors.append(error)
                records.append(record)

        return records, errors


    def save(self, output):
        print(self.triangle_distance)
