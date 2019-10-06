import logging
import os

from aerofiles import igc

from constants import IGC_HEADER, IGC_RECORDS, IGC_TIME


class Flight():

    def __init__(self, track_file):

        self.pilot_id = os.path.basename(track_file).split('.')[0]
        self.goal_distances = {}
        
        try:
            with open(track_file, 'r') as f:
                records = igc.Reader().read(f)
                zero_indexed_points = [point for subrecord in records[IGC_RECORDS] for point in subrecord]
                time_indexed_points = {point[IGC_TIME]:point for point in zero_indexed_points}
                
                self.headers = records[IGC_HEADER]
                self.points = time_indexed_points
                

        except UnicodeDecodeError:
            logging.debug('{} is not utf-8 valid, trying iso encoding'.format(track_file))
            
            # we have to try a different file encoding for people having accents in their names
            with open(track_file, 'r', encoding='iso-8859-1') as f:
                records = igc.Reader().read(f)
                zero_indexed_points = [point for subrecord in records[IGC_RECORDS] for point in subrecord]
                time_indexed_points = {point[IGC_TIME]:point for point in zero_indexed_points}

                self.headers = records[IGC_HEADER]
                self.points = time_indexed_points
        
    def __getitem__(self, time_point):
        return self.points.get(time_point, None)
