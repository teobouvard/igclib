import pickle
import json

def load_tasks(path):
    tasks = []

    with open(path, 'rb') as f:
        elem = f.read()
        tasks.append(json.loads(elem))
    
    return tasks

if __name__ == '__main__':
    tasks = load_tasks('data/tasks.pkl')
    print('hello')