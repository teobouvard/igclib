import os
from datetime import time

import pytest
from igclib.core.race import Race
from igclib.tests import TEST_DATA


@pytest.fixture(scope='module')
def xctrack_race():
	tracks = os.path.join(TEST_DATA, 'tracks', 'pwca_brazil_2019_7_few_tracks')
	task = os.path.join(TEST_DATA, 'tasks', 'pwca_brazil_2019_7.xctsk')
	race = Race(tracks=tracks, task=task, progress='gui')
	return race

@pytest.fixture(scope='module')
def b64_xctrack_race():
	tracks = os.path.join(TEST_DATA, 'tracks', 'pwca_brazil_2019_7_few_tracks')
	task = os.path.join(TEST_DATA, 'tasks', 'pwca_brazil_2019_7.b64')
	with open(task, 'r') as f:
		task_string = f.read()
	race = Race(tracks=tracks, task=task_string, progress='gui')
	return race

def test_race(xctrack_race, b64_xctrack_race):
	pass



