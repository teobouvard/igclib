from aerofiles import igc

class Flight():

    def __init__(self, track_file):
        try:
            with open(track_file, 'r') as f:
                records = igc.Reader().read(f)
                zero_indexed_points = [point for subrecord in records['fix_records'] for point in subrecord]
                time_indexed_points = {point['time']:point for point in zero_indexed_points}

                self.headers = records['header']
                self.points = time_indexed_points

        except UnicodeDecodeError:
            print('{} is not utf-8 valid'.format(track_file))
        
    
    def extract_altitudes(self):
        altitudes = [x['gps_alt'] for x in self.points]
        return altitudes