import string
import logging
import sys

def int_from_string(chars):
    return int(''.join(x for x in chars if x in string.digits))

def level_to_meters(level):
    return feets_to_meters(100*level)

def feets_to_meters(altitude):
    # http://www.sfei.org/it/gis/map-interpretation/conversion-constants
    return int(0.3048*altitude)

def parse_altitude(record):
    if record == 'SFC':
        return 0
    elif record == 'UNL':
        return sys.maxsize
    elif 'FL' in record:
        level = int_from_string(record)
        return level_to_meters(level)
    elif 'FT' and 'AMSL' in record:
        altitude = int_from_string(record)
        return feets_to_meters(altitude)
    elif 'FT' and 'AGL' in record:
        # TODO get ground level for this point
        altitude = int_from_string(record)
        return feets_to_meters(altitude)
    else:
        raise KeyError('Could not parse altitude')