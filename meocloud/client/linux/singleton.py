import fcntl
import os


class InstanceAlreadyRunning(RuntimeError):
    pass


class SingleInstance(object):
    def __init__(self, filename):
        self.initialized = False
        self.lockfile = filename
        self.fp = None

    def start(self):
        """
        Attempts to acquire the lock
        and raises and exception if it fails.
        """
        if self.initialized:
            return

        try:
            self.acquire()
        except IOError:
            raise InstanceAlreadyRunning()

        self.initialized = True

    def stop(self):
        """
        Releases the lock.
        """
        if not self.initialized:
            return

        self.release()
        self.initialized = False

    def acquire(self):
        self.fp = open(self.lockfile, 'w')
        fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def release(self):
        fcntl.lockf(self.fp, fcntl.LOCK_UN)
        if os.path.isfile(self.lockfile):
            os.unlink(self.lockfile)

    def test_lock_free(self):
        """
        Tests if the lock is not in use.
        """
        try:
            self.acquire()
        except IOError:
            return False
        else:
            self.release()
            return True
