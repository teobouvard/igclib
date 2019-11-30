###################
Command line manual
###################

.. highlight:: bash

Usage
======

::

    igclib COMMAND [OPTIONS] ARGS


Commands
========

::

    optimize

        Get the optimized version of a task.
        Required arguments :
            --task
            --output

::

    replay

        Creates a race without validating flights.
        Required arguments :
            --task
            --flights
            --output

::

    race

        Creates a race with validated flights.
        Required arguments :
            --task and --flights or --path
            --output

::

    crawl

        Crawls a provider for all events hosted in the specified year.
        Optional arguments :
            --provider [ PWCA | FFVL ] (defaults to PWCA)
            --year (defaults to current year)

::

    watch

        Get the features of a pilot on a flight.
        Required arguments :
            --path
            --pilot
            --output

Options
========

::

    --progress [ gui | ratio | silent ] (defaults to gui)

        Defines the way progress is displayed to the user.
        * gui displays a progress bar
        * ratio displays a percentage on each line
        * silent runs quietly


