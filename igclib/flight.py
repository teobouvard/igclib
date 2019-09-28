from aerofiles import igc

class Flight():

    def __init__(self, track_file):
        try:
            with open(track_file, 'r') as f:
                records = igc.Reader().read(f)
                zero_indexedpoints = [point for subrecord in records['fix_records'] for point in subrecord]
                time_indexedpoints = {point['time']:point for point in zero_indexedpoints}

                self.headers = records['header']
                self.points = time_indexedpoints

        except UnicodeDecodeError:
            print('{} is not utf-8 valid'.format(track_file))
        
    def __getitem__(self, time_point):
        return self.points.get(time_point, None)