##################################
Command line Examples
##################################

.. highlight:: bash

Build a race and save it to disk
=================================

::

    igclib --mode race --task task.xctsk --flights tracks_dir/ --output race.pkl


Get a task optimization info in json
====================================

::

    igclib --mode optimize --task task.xctsk


Get all available tasks from a provider
=======================================

::

    igclib --mode crawl --provider PWCA --year 2015
