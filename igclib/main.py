#import numpy as np
#import pandas as pd
#from matplotlib import pyplot as plt

from race import Race

tracks_dir = 'data/test'

if __name__ == '__main__':
    
    r =  Race(tracks_dir)
    f = r.flights['0011']
    print(r)
