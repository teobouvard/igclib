.PHONY: docs

dev:
	python3 igclib/main.py --race test_data/race.pkl --pilot 0035

race:
	igclib --mode race --task test_data/tasks/task.xctsk --flights test_data/one_track --output /dev/null

install:
	pip install --user -e .

docs:
	cd docs && make clean && make html && python3 -m http.server

deploy:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

ext: install
	python3 c_api_dev.py