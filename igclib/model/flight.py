import logging
import os

from aerofiles import igc

from igclib.constants import IGC_HEADER, IGC_RECORDS, IGC_TIME, IGC_PILOT_NAME
from igclib.model.geo import Point


class Flight():
    """[summary]
    
    Returns:
        [type]: [description]
    """

    def __init__(self, track_file):

        self.pilot_id = os.path.splitext(os.path.basename(track_file))[0]
        self.race_distance = None
        self.race_time = None
        
        for encoding in ['utf-8', 'iso-8859-1']:
            try:
                with open(track_file, 'r', encoding=encoding) as f:
                    records = igc.Reader().read(f)
                    self._build(records)

            except UnicodeDecodeError:
                logging.debug(f'{track_file} is not {encoding} encoded, trying something else')

        if self.points == {}:
            raise ValueError(f'{track_file} is empty or could not be read')


    def _build(self, records, encoding='utf-8'):
        self.pilot_name = str(records[IGC_HEADER][1][IGC_PILOT_NAME])
        self.points = {point[IGC_TIME]:Point(record=point) for subrecord in records[IGC_RECORDS] for point in subrecord} 
        
    def __getitem__(self, time_point):
        return self.points.get(time_point, None)

    def __str__(self):
        return self.pilot_name
