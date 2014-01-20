from gevent.event import Event, AsyncResult, Timeout
from six.moves import xrange

__all__ = ['Events', 'AsyncResults', 'DaemonState']

class AsyncResultWrapper(object):
    def __init__(self):
        self.async_result = None

    def create(self):
        if self.async_result is not None:
            assert False, 'Trying to create async_result but it is not None'
        self.async_result = AsyncResult()

    def get(self, *args, **kwargs):
        try:
            result = self.async_result.get(*args, **kwargs)
        except Timeout:
            result = None
        self.async_result = None
        return result

    def set(self, *args, **kwargs):
        if self.async_result is not None:
            self.async_result.set(*args, **kwargs)


class Events:
    shutdown_required = Event()
    state_changed = Event()
    core_start_ready = Event()


class AsyncResults:
    remote_directory_listing = AsyncResultWrapper()


class DaemonState:
    (
        AUTHORIZATION_REQUIRED,
        AUTHORIZATION_OK,
        OFFLINE,
        ROOT_FOLDER_MISSING,
    ) = xrange(4)
    current = None
