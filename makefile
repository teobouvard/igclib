data: download extract clean

download:
	# downloading current year results
	@ wget -nc -r -l 2 -A zip -erobots=off -P data/ pwca.org/results/results/

	# downloading past years results
	@ for year in $(shell seq 1990 $(shell expr $(shell date +"%Y") - 1)); do			\
	    wget -nc -r -l 2 -A zip -erobots=off -P data/ pwca.org/results/results_$$year/; \
	done 																				\

extract:
	@ for zip in $(shell find data/ -name \*.zip); 										\
	do																					\
	filename=$$(basename $$zip);														\
	year=$$(basename $$(dirname $$zip)); 												\
	zipdir=data/$$year/$${filename%.zip}; 												\
	mkdir -p $$zipdir; 																	\
	unzip -d $$zipdir $$zip; 															\
	done 																				\

clean:
	$(shell find data -type d -exec dirname {} \; | sort | uniq -u | \
	while read dir; do mv $$dir/*/*.igc $$dir; rm -rf $$dir/trk; done)
	rm -rf data/pwca.org

purge:
	rm -rf data/