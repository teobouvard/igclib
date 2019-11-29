##################################
Command line Examples
##################################

.. highlight:: bash

Build a race and save it to disk
=================================

::

    igclib race --task task.xctsk --flights tracks_dir/ --output race.pkl


Get a task optimization info in json
====================================

::

    igclib optimize --task task.xctsk --progress ratio


Get all available tasks from a provider
=======================================

::

    igclib crawl --provider PWCA --year 2015
