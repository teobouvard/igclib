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
        
        try:
            with open(track_file, 'r', encoding='iso-8859-1') as f:
                records = igc.Reader().read(f)
                self._build(records)

        except UnicodeDecodeError:
            logging.debug(f'{track_file} is not utf-8 valid, trying iso encoding')
            
            # we have to try a different file encoding for people having accents in their names
            with open(track_file, 'r', encoding='iso-8859-1') as f:
                records = igc.Reader().read(f)
                self._build(records)
    
    def _build(self, records):
        self.pilot_name = records[IGC_HEADER][1][IGC_PILOT_NAME]
        self.points = {point[IGC_TIME]:Point(record=point) for subrecord in records[IGC_RECORDS] for point in subrecord} 
        
    def __getitem__(self, time_point):
        return self.points.get(time_point, None)

    def __str__(self):
        return self.pilot_name
