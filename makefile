.PHONY: docs tests release

# ================ #
#  USEFUL TARGETS  #
# ================ #

install:
	pip3 install --user -e .

docs:
	cd docs && make clean && make html && python3 -m http.server

tests:
	pytest 

release:
	rm -f dist/*
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

# ================ #
#   DEV TARGETS    #
# ================ #

install-dev: install
	pip3 install --user -r requirements-dev.txt

format:
	yapf -ipr --verbose igclib/ 

replay:
	igclib replay --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --flights igclib/tests/test_data/tracks/pwca_brazil_2019_7_few_tracks --output saved_races/big_race.igclib

race:
	igclib race --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --flights igclib/tests/test_data/tracks/pwca_brazil_2019_7_few_tracks --output saved_races/big_race.igclib

watch:
	igclib watch --path saved_races/big_race.pkl --pilot 0093 --progress ratio

optimize:
	igclib optimize --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --progress ratio

task:
	igclib --mode optimize --task igclib/tests/test_data/tasks/task.xctsk

crawl:
	igclib --mode crawl --provider PWCA --year 2015 --progress ratio

fix-lib:
	mv $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/libz.so.1 $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/libz.so.1.old
	sudo ln -s /lib/x86_64-linux-gnu/libz.so.1 $(HOME)/.local/lib/python3.6/site-packages/pptk/libs/