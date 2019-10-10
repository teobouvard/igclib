.PHONY: docs

dev:
	python3 igclib/main.py --race test_data/race.pkl --pilot 0035

race:
	igclib --mode race --task test_data/tasks/task.xctsk --flights test_data/large_tracks  --n_jobs -1 --output test_data/race.pkl

install:
	pip install --user -e .

docs: clean-docs
	cd docs && make html && python3 -m http.server

clean-docs:
	cd docs && make clean

deploy:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*