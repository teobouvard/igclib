.PHONY: docs tests

# ================ #
#  USEFUL TARGETS  #
# ================ #

install:
	pip install --user -e .

docs:
	cd docs && make clean && make html && python3 -m http.server

tests:
	pytest --disable-pytest-warnings

dist:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

# ================ #
#   DEV TARGETS    #
# ================ #

dev:
	python3 igclib/main.py --race test_data/test.pkl --pilot 0090

race:
	igclib race --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --flights igclib/tests/test_data/tracks/pwca_brazil_2019_7_few_tracks --output saved_races/big_race.igclib

watch:
	igclib watch --path saved_races/big_race.pkl --pilot 0035

task:
	igclib --mode optimize --task igclib/tests/test_data/tasks/task.xctsk

crawl:
	igclib --mode crawl --provider PWCA --year 2015 --progress ratio

fix-lib:
	mv $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/libz.so.1 $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/libz.so.1.old
	sudo ln -s /lib/x86_64-linux-gnu/libz.so.1 $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/