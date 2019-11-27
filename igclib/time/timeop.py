# most of this mess is necessary because you can't add datetime.time objects, which are used by the aerofiles parser
from datetime import datetime, timedelta, time


def add_times(t1, t2):
    delta_hour = t1.hour + t2.hour
    delta_minute = t1.minute + t2.minute
    delta_second = t1.second + t2.second
    return time(delta_hour, delta_minute, delta_second)


def sub_times(t1, t2):
    d1 = datetime(1, 1, 1, t1.hour, t1.minute, t1.second)
    d2 = datetime(1, 1, 1, t2.hour, t2.minute, t2.second)
    delta = d1 - d2
    return (datetime.min + delta).time()


def next_second(t):
    d = datetime(1, 1, 1, t.hour, t.minute, t.second)
    d += timedelta(seconds=1)
    return d.time()


def add_offset(t, **kwargs):
    d1 = datetime(10, 10, 10, t.hour, t.minute, t.second)
    offset = d1 + timedelta(**kwargs)
    return offset.time()
