import logging
import os

from aerofiles import igc

from igclib.constants import IGC_HEADER, IGC_RECORDS, IGC_TIME, IGC_PILOT_NAME, IGC_TZ_OFFSET
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

            except UnicodeDecodeError:
                logging.debug(f'{igc_file} is not {encoding} encoded, trying something else')

        if not hasattr(self, 'points') or self.points == {}:
            raise ValueError(f'{igc_file} is empty or could not be read')


    def _build(self, records, encoding='utf-8'):
        self.pilot_name = str(records[IGC_HEADER][1][IGC_PILOT_NAME])
        self.points = {}

        time_offset = records[IGC_HEADER][1].get(IGC_TZ_OFFSET, 0)
        for subrecord in records[IGC_RECORDS]:
            for point in subrecord:
                adjusted_time = add_offset(point[IGC_TIME], hours=time_offset)
                self.points[adjusted_time] = Point(record=point, status='flying')
        
        first_timestamp = min(self.points)
        last_timestamp = max(self.points)
        self._first_point = {'timestamp':first_timestamp, 'point':self.points[first_timestamp]}
        self._last_point = {'timestamp':last_timestamp, 'point':self.points[last_timestamp]}
        

        
    def __getitem__(self, time_point):
        return self.points.get(time_point, None)

    def __str__(self):
        return self.pilot_name