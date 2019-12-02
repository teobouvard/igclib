import string
import sys


def int_from_string(chars):
    return int(''.join(x for x in chars if x in string.digits))


def level_to_meters(level):
    return feets_to_meters(100 * level)


def feets_to_meters(altitude):
    # http://www.sfei.org/it/gis/map-interpretation/conversion-constants
    return int(0.3048 * altitude)


def parse_altitude(record):
    """Returns the altitude of a record
    
    Args:
        record (str): Openair altitude record
    
    Returns:
        int, bool : The altitude and a boolean which indicates if relative to the ground
    """
    if record == 'SFC' or record == 'GND':
        return 0, False
    elif record == 'UNL':
        return sys.maxsize, False
    elif record.startswith('FL'):
        level = int_from_string(record)
        return level_to_meters(level), False
    elif record.endswith('AMSL'):
        altitude = int_from_string(record)
        return feets_to_meters(altitude), False
    elif record.endswith('AGL') or record.endswith('ASFC'):
        altitude = int_from_string(record)
        return altitude, True
    else:
        raise KeyError('Could not parse altitude')
