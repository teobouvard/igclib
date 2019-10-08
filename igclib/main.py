import logging
from pympler import asizeof

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

from race import Race

logging.basicConfig(level=logging.INFO)

TRACKS_DIR = 'test/one_track'
#TRACKS_DIR = 'test/small_tracks'
#TRACKS_DIR = 'test/large_tracks'
TASK_FILE = 'test/tasks/task0.xctsk'
#TASK_FILE = 'data/tasks/task_2019-05-12.xctsk'
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
    
    r =  Race(TRACKS_DIR, TASK_FILE)
    print(r)
    features = r.get_pilot_features(PILOT_ID)
    #animate_delta_altitude(features)
    #print(asizeof.asizeof(r) / 10e6)
    times = list(r.flights[PILOT_ID].points.keys())
    dist = list(point['goal_dist'] for point in r.flights[PILOT_ID].points.values())
    plt.plot(times, dist)
    plt.show()
