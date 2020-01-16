import string
import sys
import logging


def geo2deg(latitude, longitude):
    """
    This method assume that latitude and longitude are in one of the following formats:

    *   <geoLat>453700N</geoLat>
        <geoLong>0064554E</geoLong>

    *   <geoLat>460820.3N</geoLat>
        <geoLong>0060731.2E</geoLong>

    *   <geoLat>500605.54N</geoLat>
        <geoLong>0014952.73E</geoLong>
    """
    lat = f'{latitude[0:2]}:{latitude[2:4]}:{latitude[4:6]} {latitude[-1]}'
    lon = f'{longitude[0:3]}:{longitude[3:5]}:{longitude[5:7]} {longitude[-1]}'
    return lat, lon


def km2nm(distance):
    """
    Converts a distance from km to nautical miles
    """
    return float(distance) / 1.852


def int_from_string(chars):
    return int(''.join(x for x in chars if x in string.digits))


def level_to_meters(level):
    return feets_to_meters(100 * level)


def feets_to_meters(altitude):
    """
    http://www.sfei.org/it/gis/map-interpretation/conversion-constants
    """
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
