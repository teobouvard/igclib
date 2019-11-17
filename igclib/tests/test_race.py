import os
from datetime import time

import pytest
from igclib.model.race import Race
from igclib.tests import TEST_DATA


@pytest.fixture(scope='module')
def xctrack_race():
	tracks = os.path.join(TEST_DATA, 'tracks', 'pwca_brazil_2019_7_few_tracks')
	task = os.path.join(TEST_DATA, 'tasks', 'pwca_brazil_2019_7.xctsk')
	race = Race(tracks_dir=tracks, task_file=task, progress='gui')
	return race

@pytest.fixture(scope='module')
def b64_xctrack_race():
	tracks = os.path.join(TEST_DATA, 'tracks', 'pwca_brazil_2019_7_few_tracks')
	task_file = os.path.join(TEST_DATA, 'tasks', 'pwca_brazil_2019_7.b64')
	with open(task_file, 'r') as f:
		task_string = f.read()
	race = Race(tracks_dir=tracks, task_file=task_string, progress='gui')
	return race

def test_race(xctrack_race, b64_xctrack_race):
	pass



