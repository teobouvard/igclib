igclib
--------

Save a race to disk

    >>> from igclib.model.race import Race
    >>> r =  Race(tracks_dir='test_data/large_tracks', task_file='test_data/tasks/task.xctsk', n_jobs=-1)
    >>> r.save('test_data/race.pkl')

Load a race from disk

    >>> from igclib.model.race import Race
    >>> r =  Race(path='test_data/race.pkl')
    >>> print(r)