dev:
	python3 igclib/main.py --race test_data/race.pkl --pilot 0035

export:
	python3 igclib/bin/race_exporter.py --task test_data/tasks/task0.xctsk --flights test_data/large_tracks  --n_jobs -1 --export_path test_data/race.pkl