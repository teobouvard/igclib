import os

import pytest

from igclib.model.task import Task
from igclib.tests import TEST_DATA


def test_xctask_build():
	task = os.path.join(TEST_DATA, 'tasks', 'task.xctsk')
	t = Task(task)
	t.to_json()

def test_pwcatask_build():
	task = os.path.join(TEST_DATA, 'tasks', 'pwca_task.json')
	t = Task(task)
	t.to_json()

def test_pwcataskb64_build():
	task = os.path.join(TEST_DATA, 'tasks', 'pwca_task_b64.txt')
	with open(task, 'r') as f:
		task = f.read()
	t = Task(task)
	t.to_json()