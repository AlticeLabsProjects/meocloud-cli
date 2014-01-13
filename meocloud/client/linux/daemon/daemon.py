#! /usr/bin/env python

from meocloud.client.linux.logger import init_logging

import os
import gevent
from gevent import monkey
from subprocess import Popen

from meocloud.client.linux.settings import (CORE_LISTENER_SOCKET_ADDRESS, UI_LISTENER_SOCKET_ADDRESS,
                                            LOGGER_NAME, DAEMON_PID_PATH, DAEMON_LOCK_PATH, DEV_MODE,
                                            VERSION, DAEMON_VERSION_CHECKER_PERIOD)
from meocloud.client.linux.daemon.ui_listener import UIListener
from meocloud.client.linux.daemon.core_listener import CoreListener
from meocloud.client.linux.daemon.core_client import CoreClient
from meocloud.client.linux.daemon.core import Core
from meocloud.client.linux.db import UIConfig
from meocloud.client.linux.daemon.communication import Events
from meocloud.client.linux.singleton import SingleInstance, InstanceAlreadyRunning
from meocloud.client.linux.locations import create_required_directories
from meocloud.client.linux.cli.notifications import NotificationsHandler
from meocloud.client.linux.utils import get_own_dir


import logging

# TODO Try out http://www.python.org/dev/peps/pep-3143/#python-daemon, as it solves many problems already solved,
# probably in a better way, plus some others.


def check_own_version(log):
    if not DEV_MODE:
        own_dir = get_own_dir(__file__)
        version_path = os.path.join(own_dir, 'VERSION')
        restart_script_path = os.path.join(own_dir, 'restart_meocloud.sh')
        try:
            while True:
                gevent.sleep(DAEMON_VERSION_CHECKER_PERIOD)
                with open(version_path) as f:
                    current_version = f.read().strip()
                if current_version != VERSION:
                    log.info('There seems to have been an update and nobody told us. Will now restart!')
                    Popen(restart_script_path, close_fds=True)
                    gevent.sleep(10)
                    log.error('We should have been restarted, why are we still here?!')
                    Events.shutdown_required.set()
        except IOError:
            log.exception('check_own_version error')


def main():
    create_required_directories()
    init_logging()
    log = logging.getLogger(LOGGER_NAME)
    instance = SingleInstance(DAEMON_LOCK_PATH)
    try:
        instance.start()
    except InstanceAlreadyRunning:
        log.info('Daemon: Could not acquire single instance lock. Aborting.')
    else:
        try:
            with open(DAEMON_PID_PATH, 'w') as f:
                f.write(str(os.getpid()))
            # TODO find out why the core isn't killing itself when the daemon is killed
            # TODO maybe I should handle the SIGTERM signal?
            monkey.patch_all()
            gevent.spawn(check_own_version, log)

            # Singletons
            core_client = CoreClient()
            ui_config = UIConfig()

            notifs_handler = NotificationsHandler()

            ui_listener = UIListener(UI_LISTENER_SOCKET_ADDRESS, core_client, ui_config, notifs_handler)
            core_listener = CoreListener(CORE_LISTENER_SOCKET_ADDRESS, core_client, ui_config, notifs_handler)
            core = Core(core_client)

            # Attempt to stop core, just in case there is a dangling core running
            core.stop()
            ui_listener_greenlet = gevent.spawn(ui_listener.start)
            core_listener_greenlet = gevent.spawn(core_listener.start)
            watchdog_greenlet = gevent.spawn(core.watchdog)

            Events.shutdown_required.wait()

            log.info('Daemon: Shutting down')

            ui_listener_greenlet.kill(block=True)
            core_listener_greenlet.kill(block=True)
            watchdog_greenlet.kill(block=True)

            # Sending a shutdown to the core should be enough to gracefully kill it,
            # but it might ignore us so after a little while, kill it forcefully
            try:
                core_client.shutdown()
                gevent.sleep(1)
            except Exception:
                log.warning('Daemon: Gracefull shutdown has thrown an exception. '
                            ' Will ignore it just shut the core down forcefully.')
            core.stop()
        except Exception:
            log.exception('Daemon: An uncatched error occurred!')
        finally:
            instance.stop()


if __name__ == '__main__':
    main()
