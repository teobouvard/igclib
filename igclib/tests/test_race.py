import os

import pytest

from igclib.model.race import Race
from igclib.tests import TEST_DATA


def test_race_build():
	tracks = os.path.join(TEST_DATA, 'one_track')
	task = os.path.join(TEST_DATA, 'tasks', 'task.xctsk')
	r =  Race(tracks_dir=tracks, task_file=task, progress='silent')

def test_zip_race_build():
	tracks = os.path.join(TEST_DATA, 'one_track.zip')
	task = os.path.join(TEST_DATA, 'tasks', 'task.xctsk')
	r =  Race(tracks_dir=tracks, task_file=task, progress='silent')