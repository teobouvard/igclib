import json

class XCTask():

    def __init__(self, task_file):
        with open(task_file, 'r') as f:
            self.task_file = json.load(f)

    def read(self):
        pass