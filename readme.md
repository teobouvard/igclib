[![logo](assets/igclib_logo.svg)](https://teobouvard.github.io/)
---

[![build status](https://img.shields.io/circleci/build/github/teobouvard/igclib/master?style=flat-square)](https://circleci.com/gh/teobouvard/igclib)
[![docs status](https://img.shields.io/readthedocs/igclib?style=flat-square)](https://igclib.readthedocs.io/en/latest/)

``igclib`` is a Python module and a command line tool designed for the analysis of paragliding competitions.

## Get started

```shell
git clone https://github.com/teobouvard/igclib.git
cd igclib
make install
```

For a quick guide on how to use this library, take a look at the [documentation](https://igclib.readthedocs.io/en/latest/).

## Interesting links

[Solving the task optimization problem using Quasi-Newton methods](https://teobouvard.github.io/2019/10/20/task_optimization.html)

## Todo

* Library

    * change task validation method to closeness of next fast waypoint
    * add tests

* Data collection

    * refactor constants
    * ADD CHECKS OR RAISE FLIGHT CRAWLER FORMAT
    * superfinal result not on the same index !
    * maybe not rm downloaded tracks zip ? -> implement tracks caching in tmp dir


## Requirements

* Python 3.5 or higher
