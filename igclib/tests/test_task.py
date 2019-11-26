import os
from datetime import time

import pytest
from igclib.core.task import Task
from igclib.tests import TEST_DATA

APPROX = 0.005

@pytest.fixture(scope='session')
def xctask():
	task = os.path.join(TEST_DATA, 'tasks', 'pwca_brazil_2019_7.xctsk')
	return Task(task)

@pytest.fixture(scope='session')
def pwca_task():
	task = os.path.join(TEST_DATA, 'tasks', 'pwca_brazil_2019_7.json')
	return Task(task)

@pytest.fixture(scope='session')
def xctask_b64():
	task = os.path.join(TEST_DATA, 'tasks', 'pwca_brazil_2019_7.b64')
	with open(task, 'r') as f:
		task_string = f.read()
	return Task(task_string)

def test_task_open(xctask, xctask_b64, pwca_task):
	assert xctask.start == time(12, 40, 00)
	assert xctask_b64.start == time(12, 40, 00)
	assert pwca_task.start == time(12, 40, 00)

def test_task_open(xctask, xctask_b64, pwca_task):
	assert xctask.open == time(11, 40, 00) # open time not in file, use default
	assert xctask_b64.open == time(11, 20, 00)
	assert pwca_task.open == time(11, 20, 00)

def test_task_opti(xctask, xctask_b64, pwca_task):
	assert xctask.opti.distance == pytest.approx(94300, APPROX)
	assert xctask_b64.opti.distance == pytest.approx(94300, APPROX)
	assert pwca_task.opti.distance == pytest.approx(94300, APPROX)
	assert len(xctask) == pytest.approx(len(xctask_b64), APPROX) == pytest.approx(len(pwca_task), APPROX)
