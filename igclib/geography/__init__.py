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
        return c_distance(
            getattr(args[0], 'lat', args[0][0]),
            getattr(args[0], 'lon', args[0][1]),
            getattr(args[1], 'lat', args[1][0]),
            getattr(args[1], 'lon', args[1][1]))


def heading(*args):
    if len(args) == 4:
        return c_heading(*args)
    elif len(args) == 2:
        return c_heading(
            getattr(args[0], 'lat', args[0][0]),
            getattr(args[0], 'lon', args[0][1]),
            getattr(args[1], 'lat', args[1][0]),
            getattr(args[1], 'lon', args[1][1]))


def destination(*args):
    if len(args) == 4:
        return c_heading(*args)
    elif len(args) == 3:
        return c_destination(
            getattr(args[0], 'lat', args[0][0]),
            getattr(args[0], 'lon', args[0][1]),
            *args[1:])
