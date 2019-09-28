from aerofiles import igc

useless_info = ['comment_records', 'dgps_records', 'event_records', 'fix_record_extensions', 'k_record_extensions', 'k_records', 'logger_id', 'satellite_records', 'security_records', 'task']

class Flight():

    def __init__(self, track_file):
        try:
            with open(track_file, 'r') as f:
                records = igc.Reader().read(f)
                for info in useless_info:
                    records.pop(info, None)
                self.records = records
        except UnicodeDecodeError:
            print('{} is not utf-8 valid'.format(track_file))