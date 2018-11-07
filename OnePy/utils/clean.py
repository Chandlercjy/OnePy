from functools import wraps

import arrow


def make_it_float(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        return float(func(*args, **kargs))

    return wrapper


def make_it_datetime(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        return arrow.get(func(*args, **kargs))

    return wrapper
