import logging
import os
import json

from aerofiles import igc

from igclib.constants import IGC_HEADER, IGC_RECORDS, IGC_TIME
from igclib.model.geo import Point
from igclib.utils.json_encoder import ComplexEncoder


class Flight():
    """[summary]
    
    Returns:
        [type]: [description]
    """

    __slots__ = ['pilot_id', 'headers', 'points']

    def __init__(self, track_file):

        self.pilot_id = os.path.basename(track_file).split('.')[0]
        
        try:
            with open(track_file, 'r') as f:
                records = igc.Reader().read(f)
                self._build(records)

        except UnicodeDecodeError:
            logging.debug('{} is not utf-8 valid, trying iso encoding'.format(track_file))
            
            # we have to try a different file encoding for people having accents in their names
            with open(track_file, 'r', encoding='iso-8859-1') as f:
                records = igc.Reader().read(f)
                self._build(records)
    
    def _build(self, records):
        self.headers = records[IGC_HEADER]
        self.points = {point[IGC_TIME]:Point(record=point) for subrecord in records[IGC_RECORDS] for point in subrecord} 
        
    def __getitem__(self, time_point):
        return self.points.get(time_point, None)

    def to_json(self):
        return json.dumps(self.__dict__, cls=ComplexEncoder)
