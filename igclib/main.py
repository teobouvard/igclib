import argparse
import logging

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from pympler import asizeof

from race import Race

logging.basicConfig(format= '%(levelname)s: %(message)s', level=logging.INFO)

def animate_features(features):
    fig, (ax1, ax2) = plt.subplots(1, 2, tight_layout=True)
    plt.ioff()

    for timestamp, feature in features.items():
        timestamp = str(timestamp)
        altitudes = np.array(feature.group_relation.delta_altitude)
        goal_distances = np.array(feature.group_relation.delta_distance)
        grs = np.array(feature.group_relation.glide_ratio)  

        n_pilots = altitudes.size
        pilots_below = altitudes[altitudes > 0].size
        in_front = goal_distances[goal_distances > 0].size
        in_control = grs[grs < 10].size

        logging.info('race time : {} - {} pilots ({} below, {} in control, {} in front) '.format(timestamp, n_pilots, pilots_below, in_control, in_front))
        
        ax1.axhline(0, 0, 1)
        sns.distplot(altitudes, ax=ax1, vertical=True)
        ax1.invert_yaxis()

        ax2.axvline(0, 0, 1)
        sns.distplot(goal_distances, ax=ax2, vertical=False)
        #ax2.invert_yaxis()

        plt.pause(0.01)
        ax1.cla()
        ax2.cla()

def argument_parser():
    parser = argparse.ArgumentParser(description='igclib')
    parser.add_argument('--task', type=str, help='Task file path')    
    parser.add_argument('--flights', type=str, help='IGC tracks directory path')
    parser.add_argument('--pilot', type=str, help='Pilot ID of selected pilot')

    return parser

if __name__ == '__main__':

    # parse arguments
    parser = argument_parser()
    args = parser.parse_args()

    TASK_FILE = args.task
    TRACKS_DIR = args.flights
    PILOT_ID = args.pilot
    
    r =  Race(TRACKS_DIR, TASK_FILE)
    print(r)
    features = r.get_pilot_features(PILOT_ID)
    #animate_features(features)

    print('memory size of race : {}'.format(asizeof.asizeof(r) / 10e6))
    #times = list(r.flights[PILOT_ID].points.keys())
    #dist = list(point['goal_dist'] for point in r.flights[PILOT_ID].points.values())
    #plt.plot(times, dist)
    #plt.show()
