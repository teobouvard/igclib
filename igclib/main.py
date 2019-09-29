import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt

from race import Race

TRACKS_DIR = 'test_tracks'
#TRACKS_DIR = 'data/tracks/results/2019-09-14'
PILOT_ID = '0035'

def animate_delta_altitude(features):
    plt.figure()
    plt.ioff()

    for i, relation in enumerate(features['group_relation']):
        altitudes = np.array(relation['delta_altitude'])
        grs = np.array(relation['glide_ratio'])

        timestamp = str(features['timestamp'][i])
        n_pilots = altitudes.size
        pilots_below = altitudes[altitudes > 0].size
        in_control = grs[grs < 10].size

        print('{} - {} pilots ({} below, {} in control) '.format(timestamp, n_pilots, pilots_below, in_control))
        
        plt.axhline(0, 0, 1)
        ax = sns.distplot(altitudes, vertical=True)
        ax.invert_yaxis()
        plt.pause(0.01)
        plt.clf()

if __name__ == '__main__':
    
    r =  Race(TRACKS_DIR)
    features = r.get_pilot_features(PILOT_ID)
    animate_delta_altitude(features)
    #print(features['timestamp'])
    print(features['group_relation'][50])
