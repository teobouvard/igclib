import pickle
import json

from aerofiles import igc

def load_tasks(path):
    tasks = []

    with open(path, 'rb') as f:
        elem = f.read()
        tasks.append(json.loads(elem))
    
    return tasks

if __name__ == '__main__':
    #tasks = load_tasks('data/tasks.pkl')
    with open('data/results_2019/t_1_1/0809.igc', 'r') as f:
        flight = igc.Reader().read(f)
    
    print(flight)