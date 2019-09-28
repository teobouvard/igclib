import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from race import Race

tracks_dir = 'data/tracks/results/2019-09-12'

def extract_altitudes(flight):
    fix_records = [x for x in flight['fix_records'] if len(x) > 0]
    altitudes = [x['gps_alt'] for x in fix_records[0]]
    return altitudes

if __name__ == '__main__':
    
    r =  Race(tracks_dir)
    print(r)
