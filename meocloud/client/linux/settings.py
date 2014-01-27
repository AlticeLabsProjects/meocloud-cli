from meocloud.client.linux.utils import get_own_dir
import os

RC4_KEY = '8025c571541a64bccd00135f87dec11a83a8c5de69c94ec6b642dbdc6a2aebdd'

HOME_PATH = os.path.expanduser('~')
CONFIG_PATH = os.path.join(HOME_PATH, '.meocloud')
CLOUD_HOME_DEFAULT_PATH = os.path.join(HOME_PATH, 'MEOCloud')

DEV_MODE = os.getenv('CLD_DEV', False)
DEV_SUFFIX = '-dev'
if DEV_MODE:
    CONFIG_PATH += DEV_SUFFIX
    CLOUD_HOME_DEFAULT_PATH += DEV_SUFFIX

# TODO Find a way to set this during the build process
BETA_MODE = True

CORE_BINARY_FILENAME = 'meocloudd'
CORE_LOCK_PATH = os.path.join(CONFIG_PATH, 'daemon.lock')
CORE_PID_PATH = os.path.join(CONFIG_PATH, 'daemon.pid')

PURGEMETA_PATH = os.path.join(CONFIG_PATH, 'purgemeta')
DEBUG_ON_PATH = os.path.join(CONFIG_PATH, 'debug.on')
DEBUG_OFF_PATH = os.path.join(CONFIG_PATH, 'debug.off')

UI_CONFIG_PATH = os.path.join(CONFIG_PATH, 'ui')

UI_LISTENER_SOCKET_ADDRESS = os.path.join(UI_CONFIG_PATH, 'meocloud_ui_listener.socket')
CORE_LISTENER_SOCKET_ADDRESS = os.path.join(UI_CONFIG_PATH, 'meocloud_core_listener.socket')
DAEMON_LISTENER_SOCKET_ADDRESS = os.path.join(UI_CONFIG_PATH, 'meocloud_daemon_listener.socket')

UI_CONFIG_DB_FILE = os.path.join(UI_CONFIG_PATH, 'ui_config.yaml')

LOGGER_NAME = 'meocloud_ui'
LOG_PATH = os.path.join(UI_CONFIG_PATH, 'meocloud_ui.log')
NOTIFICATIONS_LOG_PATH = os.path.join(UI_CONFIG_PATH, 'user_notifications.log')

DAEMON_BINARY_FILENAME = 'daemon'
DAEMON_LOCK_PATH = os.path.join(UI_CONFIG_PATH, 'ui.lock')
DAEMON_PID_PATH = os.path.join(UI_CONFIG_PATH, 'ui.pid')

CLI_LOCK_PATH = os.path.join(UI_CONFIG_PATH, 'cli.lock')

# seconds
CORE_WATCHDOG_PERIOD = 20
DAEMON_VERSION_CHECKER_PERIOD = 3600

DEFAULT_NOTIFS_TAIL_LINES = 10


def _get_current_version():
    if not DEV_MODE:
        own_dir = get_own_dir(__file__)
        version_path = os.path.join(own_dir, 'VERSION')
        with open(version_path) as f:
            current_version = f.read().strip()
    else:
        current_version = '0.0.0 dev'
    return current_version

VERSION = _get_current_version()
