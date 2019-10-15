.PHONY: docs tests

# ================ #
#  USEFUL TARGETS  #
# ================ #

install:
	pip install --user -e .

docs:
	cd docs && make clean && make html && python3 -m http.server

tests:
	pytest -vv

deploy:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

# ================ #
#   DEV TARGETS    #
# ================ #

dev:
	python3 igclib/main.py --race test_data/regression.pkl --pilot 0421

race:
	igclib --mode race --task igclib/tests/test_data/tasks/task.xctsk --flights igclib/tests/test_data/small_tracks --output test.pkl

task:
	igclib --mode optimize --task igclib/tests/test_data/tasks/task.xctsk

ext: install
	python3 c_api_dev.py

devext:
	gcc -g igclib/c_ext/c_api_dev.c igclib/c_ext/vc_vector.c -o igclib/c_ext/c_dev -lm

fix-lib:
	mv $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/libz.so.1 $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/libz.so.1.old
	sudo ln -s /lib/x86_64-linux-gnu/libz.so.1 $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/