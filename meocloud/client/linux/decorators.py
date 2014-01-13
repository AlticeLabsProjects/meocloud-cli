import time


class RetryFailed(RuntimeError):
    pass


class TooManyRetries(RuntimeError):
    pass


def retry(max_tries, delay=3, backoff=2, sleep_func=None):
    """
    Based on https://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    Retries a function or method until it fails to raise a RetryFailed exception.

    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. max_tries must be at least 0, and delay
    greater than 0. sleep_func will default to time.sleep.
    """

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    if max_tries < 0:
        raise ValueError("max_tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    if sleep_func is None:
        sleep_func = time.sleep

    def decorator(f):
        def wrapper(*args, **kwargs):
            current_delay = delay
            current_try = max_tries
            while current_try > 0:
                current_try -= 1
            for current_try in range(max_tries):
                try:
                    return f(*args, **kwargs)
                except RetryFailed:
                    # Do not sleep after the last retry
                    if current_try < max_tries - 1:
                        sleep_func(current_delay) # wait...
                        current_delay *= backoff  # make future wait longer
            # No more retries
            raise TooManyRetries()
        return wrapper
    return decorator
