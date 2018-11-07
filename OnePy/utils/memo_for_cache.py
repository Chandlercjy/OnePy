from functools import wraps

from OnePy.environment import Environment


def memo(key):
    cache = Environment.cache

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key not in cache:
                cache[key] = func(*args, **kwargs)

            return cache[key]

        return wrapper

    return decorate