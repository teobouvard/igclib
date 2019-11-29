from igclib.core.flight import Flight


class XC():
    """
    XC flight
    """

    def __init__(self, tracks=None, airspace=None, progress='gui'):
        self.flight = Flight(tracks)
        self.FAI_distance = self.compute_distance(scoring='FAI')

    def compute_distance(scoring='FAI'):
        pass
