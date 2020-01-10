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
	igclib replay --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --flights igclib/tests/test_data/tracks/pwca_brazil_2019_7_few_tracks --output dev_files/replay.pkl dev_files/replay.json

race:
	igclib race --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --flights igclib/tests/test_data/tracks/pwca_brazil_2019_7_all_tracks --output dev_files/race.pkl

xc:
	igclib xc --flight igclib/tests/test_data/tracks/xc_col_agnel.igc --airspace igclib/tests/test_data/airspace/france_airspace.txt --output dev_files/xc_flight.json

convert:
	igclib convert --from_format aixm --to_format openair --input_file dev_files/airspace_aixm.xml --output_file dev_files/airspace_openair.txt

watch:
	igclib watch --path dev_files/race.pkl --pilot all --output dev_files/watchxav.json

optimize:
	igclib optimize --task igclib/tests/test_data/tasks/pwca_brazil_2019_7.xctsk --output dev_files/optimized.json

crawl:
	igclib crawl --provider PWCA --year 2015 --output -