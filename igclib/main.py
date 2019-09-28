import seaborn as sns
from matplotlib import pyplot as plt

from race import Race

#TRACKS_DIR = 'data/test'
TRACKS_DIR = 'data/tracks/results/2019-05-26'

def animate_delta_altitude(features):
    plt.figure()
    plt.ioff()

    for each_second in features['group_relation']:
        delta = [relation['delta_altitude'] for pilot, relation in each_second.items()]
        sns.distplot(delta, hist=False, kde_kws = {'shade': True, 'linewidth': 3})
        plt.axvline(0, 0, 1)
        plt.pause(0.001)
        plt.clf()

if __name__ == '__main__':
    
    r =  Race(TRACKS_DIR)
    features = r.pilot_features('0010')
    animate_delta_altitude(features)
