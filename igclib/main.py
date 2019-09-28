#import numpy as np
import pandas as pd
#from matplotlib import pyplot as plt
from datetime import time

from race import Race

tracks_dir = 'data/test'



if __name__ == '__main__':
    
    r =  Race(tracks_dir)
    r.pilot_features('0011')
    print('c')
