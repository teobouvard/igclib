igclib
--------

Save a race to disk

    >>> from igclib.model.race import Race
    >>> r =  Race(tracks_dir='data/tracks', task_file='data/task', n_jobs=-1)
    >>> r.save('data/race.pkl')

Load a race from disk

    >>> from igclib.model.race import Race
    >>> r =  Race(path='data/race.pkl')
    >>> print(r)