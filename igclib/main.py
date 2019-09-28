#from matplotlib import pyplot as plt

from race import Race

TRACKS_DIR = 'data/test'


if __name__ == '__main__':
    
    r =  Race(TRACKS_DIR)
    features = r.pilot_features('0011')