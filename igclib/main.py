#import numpy as np
#import pandas as pd
#from matplotlib import pyplot as plt
from datetime import time

from race import Race

tracks_dir = 'data/test'

if __name__ == '__main__':
    
    r =  Race(tracks_dir)

    test_time = time(14,55,15)
    f = r[test_time]
    print(f)
