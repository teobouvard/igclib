import logging
import os
from datetime import time
from functools import lru_cache

from aerofiles import igc
from igclib.constants import (IGC_HEADER, IGC_PILOT_NAME, IGC_RECORDS,
                              IGC_TIME, IGC_TZ_OFFSET)
from igclib.geography.geo import Point
from igclib.time.timeop import add_offset


class Flight():
    """Class representing a Flight

    """

    def __init__(self, igc_file):

        self.pilot_id = os.path.splitext(os.path.basename(igc_file))[0]
        self.race_distance = None
        self.race_time = None

        for encoding in ['utf-8', 'iso-8859-1']:
            try:
                with open(igc_file, 'r', encoding=encoding) as f:
                    records = igc.Reader().read(f)
                    self._build(records)
                    break

            except UnicodeDecodeError:
                logging.debug(f'{igc_file} is not {encoding} encoded, trying something else')

        # if file could not be decoded, it does not have a point attribute
        if not hasattr(self, 'points') or self.points == {}:
            raise ValueError(f'{igc_file} is empty or could not be read')

    def _build(self, records):
        self.pilot_name = str(records[IGC_HEADER][1][IGC_PILOT_NAME])
        self.points = {}

        time_offset = records[IGC_HEADER][1].get(IGC_TZ_OFFSET, 0)
        for subrecord in records[IGC_RECORDS]:
            for point in subrecord:
                adjusted_time = add_offset(point[IGC_TIME], hours=time_offset)
                self.points[adjusted_time] = Point(record=point, status='flying')

        first_timestamp = min(self.points)
        last_timestamp = max(self.points)
        self._first_point = {'timestamp': first_timestamp, 'point': self.points[first_timestamp]}
        self._last_point = {'timestamp': last_timestamp, 'point': self.points[last_timestamp]}

    def __getitem__(self, key):
        if isinstance(key, time):
            return self.points.get(key, None)
        elif isinstance(key, int):
            return self.to_list()[key]
        else:
            raise ValueError(f'key must be of type int or time but is {type(key)}')

    # we should probably used @cached_property but it only exists in python >= 3.8
    @lru_cache()
    def to_list(self):
        return list(self.points.values())

    def __str__(self):
        return self.pilot_name

    def __len__(self):
        return len(self.to_list())
