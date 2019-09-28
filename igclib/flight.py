from aerofiles import igc

class Flight():

    def __init__(self, track_file):
        try:
            with open(track_file, 'r') as f:
                records = igc.Reader().read(f)
                zero_indexed_points = [point for subrecord in records['fix_records'] for point in subrecord]
                time_indexed_points = {point['time']:point for point in zero_indexed_points}

                self._headers = records['header']
                self._points = time_indexed_points

        except UnicodeDecodeError:
            print('{} is not utf-8 valid'.format(track_file))
        
    def __getitem__(self, time_point):
        return self._points.get(time_point, None)
    
    def extract_altitudes(self):
        return [x['gps_alt'] for x in self._points]