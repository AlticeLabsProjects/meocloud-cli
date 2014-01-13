class CoreOfflineException(RuntimeError):
    pass


class AlreadyRunningException(RuntimeError):
    def __init__(self, pid):
        self.pid = pid


class ListenerConnectionFailedException(RuntimeError):
    pass


class TimeoutException(RuntimeError):
    pass
