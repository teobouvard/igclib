# igclib

[![Actions Status](https://github.com/teobouvard/igclib/workflows/build/badge.svg)](https://github.com/teobouvard/igclib/actions)

## Get started

```{shell}
git clone https://github.com/teobouvard/igclib.git
cd igclib
make install
```
---

## Useful links

[Documentation (in progress)](https://igclib.readthedocs.io/en/latest/)

---
## Basic user manual

### Build a race and save it to disk

From the `igclib` executable (installed in your path during pip install)

```shell
igclib --mode race --task test_data/tasks/task.xctsk --flights test_data/large_tracks  --n_jobs -1 --output test_data/race.pkl
```

or from a Python shell

```python
from igclib.model.race import Race
r =  Race(tracks_dir='test_data/large_tracks', task_file='test_data/tasks/task.xctsk', n_jobs=-1)
r.save('test_data/race.pkl')
```

### Load a race

From a Python shell

```python
from igclib.model.race import Race
r =  Race(path='test_data/race.pkl')
```

### Get a task optimization info in json

From the `igclib` executable

```shell
igclib --mode optimize --task test_data/tasks/task.xctsk
```

### Get all available PWCA tasks from 2015

From the `igclib` executable

```shell
igclib --mode crawl --provider PWCA --year 2015
```

or from a Python shell

```python
from igclib.crawlers.task_crawler import TaskCrawler
tc = TaskCrawler(provider='PWCA', year=2015)
tasks = tc.crawl()
```

---

## Build and view the documentation

Once installed, run `make docs` and go to http://0.0.0.0:8000/build/html/

---

## Todo

### Library

* safety check on task and tracks 
* write native code for distance calculation
* remember entry start check will not work without a turnpoint inside
* add tests

### Optimizer

* when going out of a concentric turnpoint, optimized point depends on the distance of the pilot from the center, and not only of the angles
* is a real optimizer necessary ? only need a continuous distance function from start to goal

### Data collection

* parallellize requests when fetching data

### Misc

---

## Requirements

* Python 3.6 or higher (Python 3.5 will NOT work because of await list comprehensions)
