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
    if record == 'SFC' or record == 'GND':
        return 0
    elif record == 'UNL':
        return sys.maxsize
    elif record.startswith('FL'):
        level = int_from_string(record)
        return level_to_meters(level)
    elif record.endswith('AMSL'):
        altitude = int_from_string(record)
        return feets_to_meters(altitude)
    elif record.endswith('AGL') or record.endswith('ASFC'):
        # TODO get ground level for this point
        #logging.warn('no ground altitude')
        altitude = int_from_string(record)
        return feets_to_meters(altitude)
    else:
        raise KeyError('Could not parse altitude')