import argparse
import logging
import multiprocessing
multiprocessing.set_start_method('fork', True)

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from pympler import asizeof
from datetime import time

from igclib.model.race import Race

logging.basicConfig(filename='log.txt', format= '%(levelname)s: %(message)s', level=logging.INFO)

def plot_kernel(race, features):
    fig, (ax1, ax2) = plt.subplots(1, 2, tight_layout=True)
    plt.ioff()

    for timestamp, feature in features.items():
        if timestamp < race.task.start:
            continue

        t = str(timestamp)
        altitudes = np.array(feature.group_relation.delta_altitude)
        goal_distances = np.array(feature.group_relation.delta_distance)
        grs = np.array(feature.group_relation.glide_ratio)  

        n_pilots = altitudes.size
        pilots_below = altitudes[altitudes > 0].size
        in_front = goal_distances[goal_distances > 0].size
        in_control = grs[grs < 10].size

        logging.info('race time : {} - {} pilots ({} below, {} in control, {} in front) '.format(t, n_pilots, pilots_below, in_control, in_front))
        
        ax1.axhline(0, 0, 1)
        sns.distplot(altitudes, ax=ax1, vertical=True, bins=10)

        ax2.axvline(0, 0, 1)
        sns.distplot(goal_distances, ax=ax2, vertical=False, bins=10)

        plt.pause(0.01)
        ax1.cla()
        ax2.cla()

def plot_evolution(features):

    mean_altitudes = []
    mean_goal = []
    timestamps = list(features.keys())

    for feature in features.values():
        altitudes = np.array(feature.group_relation.delta_altitude)
        goal_distances = np.array(feature.group_relation.delta_distance)

        mean_altitudes.append(altitudes.mean())
        mean_goal.append(goal_distances.mean())
        
    gradient_altitudes = np.gradient(altitudes)
    gradient_goal = np.gradient(goal_distances)
        

    fig, ax = plt.subplots(2, 2, tight_layout=True, sharex=True)

    sns.lineplot(x=timestamps, y=mean_altitudes, ax=ax[0, 0])
    sns.lineplot(x=timestamps, y=mean_goal, ax=ax[1, 0])
    sns.lineplot(x=timestamps, y=gradient_altitudes, ax=ax[0, 1])
    sns.lineplot(x=timestamps, y=gradient_goal, ax=ax[1, 1])

    plt.show()

def argument_parser():
    parser = argparse.ArgumentParser(description='igclib - dev module')
    parser.add_argument('--race', required=True, type=str, help='Path to the pickled race')
    parser.add_argument('--pilot', required=True, type=str, help='Pilot ID of selected pilot')

    return parser

if __name__ == '__main__':

    # parse arguments
    parser = argument_parser()
    args = parser.parse_args()

    RACE_FILE = args.race
    PILOT_ID = args.pilot
    
    r =  Race(path=RACE_FILE)
    print(r)
    features = r.get_pilot_features(PILOT_ID)
    #plot_kernel(r, features)
    plot_evolution(features)

    #print('memory size of race : {}'.format(asizeof.asizeof(r) / 10e6))
    #times = list(r.flights[PILOT_ID].points.keys())
    #dist = list(point['goal_dist'] for point in r.flights[PILOT_ID].points.values())
    #plt.plot(times, dist)
    #plt.show()
