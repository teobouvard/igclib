# igclib

## Get started

```{shell}
# Shitty cartopy requirements, will disappear once optimizer is built
apt-get install python3-dev libproj-dev proj-data proj-bin libgeos-dev

pip3 install wheel virtualenv cython 
git clone https://github.com/teobouvard/igclib.git
cd igclib
python3 -m venv venv
source venv/bin/activate
pip3 install -e .

make export
make dev
```
## Usage


## Data collection

To fetch the IGC tracks, run `python3 crawlers/crawler_tracks.py`  
To fetch the tasks, run `python3 crawlers/crawler_tasks.py`

## Todo

### Library

* safety check on task and tracks 
* add other features to ```pilot_features()```
* write native code for distance calculation
* remember entry start check will not work without a turnpoint inside

### Optimizer

* when going out of a concentric turnpoint, optimized point depends on the distance of the pilot from the center, and not only of the angles
* is a real optimizer necessary ? only need a continuous distance function from start to goal

### Data collection

* parallellize requests when fetching data
* merge tasks and tracks


### Misc

* remove cython from fast install when cartopy is not needed anymore

## Requirements

* Python 3.6 or higher