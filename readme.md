# igclib

[![build status](https://img.shields.io/circleci/build/github/teobouvard/igclib/master?style=flat-square)](https://circleci.com/gh/teobouvard/igclib)
[![docs status](https://img.shields.io/readthedocs/igclib?style=flat-square)](https://igclib.readthedocs.io/en/latest/)

## Get started

```shell
git clone https://github.com/teobouvard/igclib.git
cd igclib
make install
```
---

## Useful links

[Documentation (in progress)](https://igclib.readthedocs.io/en/latest/)

---

## Build the documentation locally

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


### Misc

---

## Requirements

* Python 3.6 or higher (Python 3.5 will NOT work because of await list comprehensions)
