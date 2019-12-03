"""
This module contains the base classes representing a GeoPoint, a Turnpoint and an Opti.
It also provides convenience wrappers around C extension function calls.
These wrappers allow for more concise function calls to improve readability.

.. automodule:: igclib.geography.geo
    :members:
"""

from geolib import destination as c_destination
from geolib import distance as c_distance
from geolib import heading as c_heading


def distance(*args):
    if len(args) == 4:
        return c_distance(*args)
    elif len(args) == 2:
        return c_distance(*args[0], *args[1])


def heading(*args):
    if len(args) == 4:
        return c_heading(*args)
    elif len(args) == 2:
        return c_heading(*args[0], *args[1])


def destination(*args):
    if len(args) == 4:
        return c_heading(*args)
    elif len(args) == 3:
        return c_destination(*args[0], *args[1:])
