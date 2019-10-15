import os

import pytest

from igclib.model.task import Task
from igclib.tests import TEST_DATA


def test_task_build():
	task = os.path.join(TEST_DATA, 'tasks', 'task.xctsk')
	t = Task(task)
	t.to_json()
