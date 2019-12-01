"""
This module contains the base classes representing a Point, a Turnpoint and an Opti.
It also provides convenience wrappers around C extension function calls. 
These wrappers allow for more concise function calls without loss of readability.

.. automodule:: igclib.geography.geo
    :members:
"""

from geolib import distance as c_distance
from geolib import heading as c_heading
from geolib import destination as c_destination


def distance(*args):
    if len(args) == 4:
        return c_distance(*args)
    elif len(args) == 2:
        for arg in args:
            if not hasattr(arg, 'lat') or not hasattr(arg, 'lon'):
                raise ValueError('Distance arguments must have lat and lon attributes')
        return c_distance(args[0].lat, args[0].lon, args[1].lat, args[1].lon)


def heading(*args):
    if len(args) == 4:
        return c_heading(*args)
    elif len(args) == 2:
        for arg in args:
            if not hasattr(arg, 'lat') or not hasattr(arg, 'lon'):
                raise ValueError('Heading arguments must have lat and lon attributes')
        return c_heading(args[0].lat, args[0].lon, args[1].lat, args[1].lon)


def destination(*args):
    if len(args) == 4:
        return c_heading(*args)
    elif len(args) == 3:
        if not hasattr(args[0], 'lat') or not hasattr(args[0], 'lon'):
            raise ValueError('Heading arguments must have lat and lon attributes')
        return c_destination(args[0].lat, args[0].lon, *args[1:])
