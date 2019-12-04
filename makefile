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
	igclib replay --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --flights igclib/tests/test_data/tracks/pwca_brazil_2019_7_few_tracks --output saved_races/replay.pkl saved_races/replay.json

race:
	igclib race --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --flights igclib/tests/test_data/tracks/pwca_brazil_2019_7_all_tracks --output saved_races/race.pkl

xc:
	igclib xc --flight igclib/tests/test_data/tracks/xc_col_agnel.igc --airspace igclib/tests/test_data/airspace/france_airspace.txt --output saved_races/xc_flight.json

watch:
	igclib watch --path saved_races/race.pkl --pilot all --output saved_races/watchxav.json

optimize:
	igclib optimize --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --output saved_races/optimized.json

crawl:
	igclib crawl --provider PWCA --year 2015 --output -