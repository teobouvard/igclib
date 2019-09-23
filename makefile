data: download extract clean

download:
	echo 'Downloading current year results'
	@ wget -nc -r -l 2 -A zip -erobots=off -P data/ pwca.org/results/results/

	echo 'Downloading past years results'
	@ for year in $(shell seq 1990 2018); do											\
	    wget -nc -r -l 2 -A zip -erobots=off -P data/ pwca.org/results/results_$$year/; 	\
	done 																				\

extract:
	@for zip in $(shell find data/ -name \*.zip); 										\
	do																					\
	filename=$$(basename $$zip);														\
	year=$$(basename $$(dirname $$zip)); 												\
	zipdir=data/$$year/$${filename%.zip}; 												\
	mkdir -p $$zipdir; 																	\
	unzip -d $$zipdir $$zip; 															\
	done 																				\

clean:
	rm -rf data/pwca.org

purge:
	rm -rf data/