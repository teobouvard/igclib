dev:
	python3 igclib/main.py --race test_data/race.pkl --pilot 0035

export:
	python3 igclib/bin/race_export --task test_data/tasks/task.xctsk --flights test_data/large_tracks  --n_jobs -1 --export test_data/race0.pkl

install:
	pip install --user -e .