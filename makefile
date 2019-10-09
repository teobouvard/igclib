dev:
	python3 igclib/main.py --race data/race.pkl --pilot 0035

export:
	python3 igclib/race_exporter.py --task test/tasks/task0.xctsk --flights test/small_tracks  --n_jobs -1 --export_path data/race.pkl