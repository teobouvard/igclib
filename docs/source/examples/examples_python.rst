##################################
Python Examples
##################################


Build a race and save it to disk
=================================

::

    from igclib.model.race import Race

    r =  Race(tracks_dir='tracks/', task_file='task.xctsk')
    r.save('race.pkl')


Load a race
===========

::

    from igclib.model.race import Race

    r =  Race(path='race.pkl')


Get a task optimization info in json
====================================

::

    from igclib.model.task import Task

    t = Task('task.xctsk')


Get all available tasks from a provider
=======================================

::

    from igclib.crawlers.task_crawler import TaskCrawler

    tc = TaskCrawler(provider='PWCA', year=2015)
    tasks = tc.crawl()
    print(tasks)
