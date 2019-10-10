# igclib

[![Actions Status](https://github.com/teobouvard/igclib/workflows/build/badge.svg)](https://github.com/teobouvard/igclib/actions)

## Get started

```{shell}
git clone https://github.com/teobouvard/igclib.git
cd igclib
pip install --user -e .
```
---

## Basic usage

### Save a Race to disk

From an executable script (installed in your path during pip install)

```console
race_export --task test_data/tasks/task.xctsk --flights test_data/large_tracks  --n_jobs -1 --export test_data/race.pkl
```

or from a Python shell

```{python}
>>> from igclib.model.race import Race
>>> r =  Race(tracks_dir='test_data/large_tracks', task_file='test_data/tasks/task.xctsk', n_jobs=-1)
>>> r.save('test_data/race.pkl')
```

### Load a Race

From a Python shell

```{ipython}
>>> from igclib.model.race import Race
>>> r =  Race(path='test_data/race.pkl')
```

---

## Data collection

To fetch the IGC tracks, run `python3 crawlers/crawler_tracks.py`  
To fetch the tasks, run `python3 crawlers/crawler_tasks.py`

---

## Todo

### Library

* safety check on task and tracks 
* add other features to ```pilot_features()```
* write native code for distance calculation
* remember entry start check will not work without a turnpoint inside
* add tests

### Optimizer

* when going out of a concentric turnpoint, optimized point depends on the distance of the pilot from the center, and not only of the angles
* is a real optimizer necessary ? only need a continuous distance function from start to goal

### Data collection

* parallellize requests when fetching data
* merge tasks and tracks

### Misc

---

## Requirements

* Python 3.5 or higher