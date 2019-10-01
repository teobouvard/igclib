import logging
from pympler import asizeof

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

from race import Race

logging.basicConfig(level=logging.ERROR)

TRACKS_DIR = 'test_tracks'
#TRACKS_DIR = 'data/tracks/results/2019-09-14'
PILOT_ID = '0035'

def animate_delta_altitude(features):
    plt.figure()
    plt.ioff()

    for timestamp, feature in features.items():
        altitudes = np.array(feature.group_relation.delta_altitude)
        grs = np.array(feature.group_relation.glide_ratio)
        timestamp = str(timestamp)

        n_pilots = altitudes.size
        pilots_below = altitudes[altitudes > 0].size
        in_control = grs[grs < 10].size

        logging.info('race time : {} - {} pilots ({} below, {} in control) '.format(timestamp, n_pilots, pilots_below, in_control))
        
        plt.axhline(0, 0, 1)
        ax = sns.distplot(altitudes, vertical=True)
        ax.invert_yaxis()
        plt.pause(0.01)
        plt.clf()

if __name__ == '__main__':
    
    r =  Race(TRACKS_DIR)
    print(r)
    features = r.get_pilot_features(PILOT_ID)
    #animate_delta_altitude(features)
    #print(asizeof.asizeof(r) / 10e6)
