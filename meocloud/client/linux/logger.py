import os
import logging
import logging.handlers
from meocloud.client.linux.settings import (LOGGER_NAME, LOG_PATH, DEBUG_ON_PATH,
                                            DEBUG_OFF_PATH, DEV_MODE, BETA_MODE)


def init_logging():
    debug_off = os.path.isfile(DEBUG_OFF_PATH)

    if debug_off:
        try:
            os.remove(DEBUG_ON_PATH)
        except OSError:
            pass
    elif DEV_MODE or BETA_MODE:
        logger = logging.getLogger(LOGGER_NAME)
        logger.propagate = False
        fmt_str = '%(asctime)s %(levelname)s %(process)d %(message)s'
        formatter = logging.Formatter(fmt_str)
        # (automatically rotated every week)
        handler = logging.handlers.TimedRotatingFileHandler(LOG_PATH, when='W6', backupCount=1)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        # touch
        with open(DEBUG_ON_PATH, 'a'):
            pass
