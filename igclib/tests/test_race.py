import os
from datetime import time

import pytest
from igclib.core.race import Race
from igclib.tests import TEST_DATA


@pytest.fixture(scope='session')
def xctrack_replay(tmpdir_factory):
    tracks = os.path.join(TEST_DATA, 'tracks', 'pwca_brazil_2019_7_few_tracks')
    task = os.path.join(TEST_DATA, 'tasks', 'pwca_brazil_2019_7.xctsk')
    replay = Race(tracks=tracks, task=task, progress='gui', validate=False)
    fn = tmpdir_factory.mktemp('generated_data')
    replay.save(os.path.join(str(fn), 'replay.igclib'))
    return fn


@pytest.fixture(scope='module')
def race_from_replay(xctrack_replay):
    race = Race(path=os.path.join(str(xctrack_replay), 'replay.pkl'))
    return race


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


def test_race(xctrack_race, b64_xctrack_race, race_from_replay):
    task_length = len(xctrack_race.task)
    assert task_length == pytest.approx(94270, abs=10)
    assert xctrack_race.n_pilots == b64_xctrack_race.n_pilots == race_from_replay.n_pilots
    assert set(xctrack_race.ranking.pilots_in_goal) == set(b64_xctrack_race.ranking.pilots_in_goal) == set(race_from_replay.ranking.pilots_in_goal) == set(['0046', '0093', '1611'])
    assert xctrack_race.ranking['0093']['distance'] == pytest.approx(task_length, abs=10)
    assert b64_xctrack_race.ranking['0093']['distance'] == pytest.approx(task_length, abs=10)
    assert race_from_replay.ranking['0093']['distance'] == pytest.approx(task_length, abs=10)
