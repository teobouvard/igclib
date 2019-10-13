.PHONY: docs

dev:
	python3 igclib/main.py --race test_data/regression.pkl --pilot 0090

race:
	igclib --mode race --task test_data/tasks/task.xctsk --flights test_data/large_tracks --output test_data/regression.pkl

install:
	pip install --user -e .

docs:
	cd docs && make clean && make html && python3 -m http.server

deploy:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

ext: install
	python3 c_api_dev.py

devext:
	gcc -g igclib/c_ext/c_api_dev.c igclib/c_ext/vc_vector.c -o igclib/c_ext/c_dev -lm