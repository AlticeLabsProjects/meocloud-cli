from six.moves import input
from six import print_
from subprocess import Popen
import socket
import signal
import errno
import time
import sys
import os

from meocloud.client.linux.protocol.daemon_ui.ttypes import State, InitResult

from meocloud.client.linux.settings import (
    BIN_DIR,
    CLOUD_HOME_DEFAULT_PATH,
    CORE_BINARY_FILENAME,
    CORE_PID_PATH,
    DAEMON_BINARY_FILENAME,
    DAEMON_PID_PATH,
    LOGGER_NAME,
    NOTIFICATIONS_LOG_PATH,
    PURGEMETA_PATH,
    VERSION,
    )
from meocloud.client.linux.exceptions import (CoreOfflineException, AlreadyRunningException,
                                              ListenerConnectionFailedException, TimeoutException)
from meocloud.client.linux.utils import test_already_running, tail, get_own_dir, get_proxy, set_proxy, get_ratelimits, set_ratelimits
from meocloud.client.linux.decorators import retry, RetryFailed, TooManyRetries
from meocloud.client.linux.db import UIConfig

# Logging
import logging
log = logging.getLogger(LOGGER_NAME)

MAX_RETRIES = 10


def human_readable_seconds(n):
    time_units = [(60, 'minute'), (60, 'hour'), (24, 'day')]
    final_unit_name = 'second'
    for unit_size, unit_name in time_units:
        if n >= unit_size:
            n //= unit_size
            final_unit_name = unit_name
        else:
            break
    if n != 1:
        final_unit_name += 's'
    return '{0} {1}'.format(n, final_unit_name)


def human_readable_bytes(n, per_second=False):
    final_unit_name = 'TB'
    for bytes_unit in [' bytes', 'KB', 'MB', 'GB']:
        if -1024.0 < n < 1024.0:
            final_unit_name = bytes_unit
            break
        n /= 1024.0
    if per_second:
        return '{0:3.1f} {1}/s'.format(n, final_unit_name)
    return '{0:3.1f}{1}'.format(n, final_unit_name)


def check_daemon_version(f):
    def wrapper(self, *args, **kwargs):
        try:
            daemon_version = self.daemon_client.version()
        except (socket.timeout, ListenerConnectionFailedException):
            # Daemon is not running or we can't contact it
            pass
        else:
            if daemon_version != VERSION:
                self.out('Your MEO Cloud daemon is outdated, will attempt to restart it.')
                self.stop()
                self.start()
        return f(self, *args, **kwargs)
    return wrapper


def daemon_must_be_running(f):
    @retry(max_tries=3, delay=1, backoff=2)
    def pinger(self):
        try:
            self.daemon_client.ping()
        except socket.timeout:
            log.warning('daemon_must_be_running: ping has timed-out, '
                        'will try to kill the daemon and retry pinging')
            self.stop(quiet=True)
            raise RetryFailed()

    @check_daemon_version
    def wrapper(self, *args, **kwargs):
        try:
            pinger(self)
        except TooManyRetries:
            log.error('Failed to ping daemon even after killing and restarting it!')
            self.out('Failed to connect to daemon.')
            self.out('Try again, and if the error persists, please contact support.')
        except ListenerConnectionFailedException:
            self.out('MEO Cloud does not seem to be running.')
            self.out('Please start it first with "meocloud start"')
            # Just in case it is running but just not answering our calls...
            self.stop(quiet=True)
        else:
            return f(self, *args, **kwargs)
    return wrapper


def exceptions_handled(f):
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except ListenerConnectionFailedException:
            self.out('Unable to connect to deamon.')
            self.out('Please try again and if it still does not work, stop meocloud and start it again.')
        except (socket.timeout, TimeoutException):
            self.out('Connection to daemon timed out.')
            self.out('Please try again and if it still does not work, stop meocloud and start it again.')
        except (EOFError, KeyboardInterrupt):
            self.out()
            self.out('Goodbye!')
    return wrapper


class CLIHandler(object):
    def __init__(self, daemon_client):
        self.daemon_client = daemon_client
        self.ui_config = UIConfig()

    def _daemon_already_running(self):
        return test_already_running(DAEMON_PID_PATH, DAEMON_BINARY_FILENAME)

    def _core_already_running(self):
        return test_already_running(CORE_PID_PATH, CORE_BINARY_FILENAME)

    def _start_daemon(self):
        pid = self._daemon_already_running()
        if pid:
            if self._core_already_running():
                raise AlreadyRunningException(pid)
            else:
                log.warning('CLIHandler._start_daemon: Core is not running and we don\'t know why. '
                            'Just in case, we\'ll stop the daemon too and continue as if nothing happened.')
                self.stop(quiet=True)
        self._handle_dying_message()
        log.info('Starting daemon')
        daemon_binary_path = os.path.join(sys.prefix, BIN_DIR, DAEMON_BINARY_FILENAME)
        self.process = Popen([daemon_binary_path], preexec_fn=lambda: os.setpgrp())
        # Try pinging daemon to make sure the listener is on
        self.daemon_client.attemptFirstConnection()

    def _handle_dying_message(self):
        dying_message = self.ui_config.get('dying_message')
        if dying_message:
            self.out('It looks like the daemon has gone and died while you were not looking...\n'
                     'Fortunately it left you with the following dying message:\n\n'
                     '---------------- DYING MESSAGE ----------------\n{0}\n'
                     '---------------- END DYING MESSAGE ----------------\n'.format(dying_message))
            self.ui_config.unset('dying_message')

    def _handle_cloud_home(self):
        cloud_home = self.ui_config.get('cloud_home')
        if not cloud_home:
            success = False
            default_cloud_home = os.path.join(os.getenv('HOME'), CLOUD_HOME_DEFAULT_PATH)
            while not success:
                cloud_home = self.ask('Which folder do you want to use as your MEO Cloud folder', default=default_cloud_home)
                force_create = False
                force_merge = False
                force_relative = False
                last_state = None
                # Keep trying the same path as long as some option has changed
                while last_state != (force_create, force_merge, force_relative):
                    last_state = (force_create, force_merge, force_relative)
                    result = self.setCloudHome(cloud_home, force_create, force_merge, force_relative)
                    if result == 'OK':
                        self.out('The selected folder will be used as your MEO Cloud folder')
                        success = True
                    elif result == 'OK_FOLDER_CREATED':
                        self.out('The selected folder was created and will be used as your MEO Cloud folder')
                        success = True
                    elif result == 'PATH_IS_FILE':
                        self.out('The given path contains a file which is preventing the creation of you MEO Cloud folder.')
                    elif result == 'FOLDER_NOT_FOUND':
                        self.out('The selected folder does not exist.')
                        force_create = self.ask_yes_no('Create it', default_yes=True)
                    elif result == 'PATH_TO_FOLDER_NOT_FOUND':
                        self.out('Multiple folders in the given path do not exist.')
                        force_create = self.ask_yes_no('Do you want them to be created')
                    elif result == 'RELATIVE_PATH':
                        abspath = os.path.abspath(cloud_home)
                        self.out('You provided a relative path which corresponds to the absolute path: {0}'.format(abspath))
                        force_relative = self.ask_yes_no('Are you sure this is the path you want')
                    elif result == 'PERMISSION_DENIED':
                        self.out('You do not have permissions to create a folder in that path.')
                    elif result == 'INVALID_PATH':
                        self.out('The given path is not a correct path, please review it.')
                    elif result == 'FOLDER_HAS_CONTENT':
                        self.out('The selected folder has content inside. If you want to use it, the contents will be synchronized to your account.')
                        force_merge = self.ask_yes_no('Are you sure you want to use it')
                    else:
                        # TODO improve error handling
                        assert False

    def setCloudHome(self, cloud_home, force_create, force_merge, force_relative):
        must_create = False
        cloud_home = os.path.normpath(cloud_home)

        if not force_relative and not cloud_home.startswith('/'):
            return 'RELATIVE_PATH'

        cloud_home = os.path.abspath(cloud_home)

        try:
            current_path = cloud_home
            while current_path != '/':
                if os.path.exists(current_path):
                    if not os.path.isdir(current_path):
                        return 'PATH_IS_FILE'
                    break
                current_path = os.path.dirname(current_path)

            if os.path.exists(cloud_home):
                if os.listdir(cloud_home):
                    if force_merge:
                        rv = 'OK'
                    else:
                        return 'FOLDER_HAS_CONTENT'
                else:
                    rv = 'OK'
            else:
                parent_dir = os.path.dirname(cloud_home)
                if force_create:
                    must_create = True
                    rv = 'OK_FOLDER_CREATED'
                else:
                    if os.path.exists(parent_dir):
                        return 'FOLDER_NOT_FOUND'
                    else:
                        return 'PATH_TO_FOLDER_NOT_FOUND'

            if must_create:
                os.makedirs(cloud_home)
                os.chmod(cloud_home, 0700)

        except OSError as os_err:
            if os_err.errno == errno.EACCES:
                return 'PERMISSION_DENIED'
            return 'INVALID_PATH'

        if rv in ('OK', 'OK_FOLDER_CREATED'):
            self.ui_config.set('cloud_home', cloud_home)
        return rv

    def _handle_client_registration(self):
        device_name = self.ask('What\'s your device name', default=socket.gethostname())
        url = self.daemon_client.authorizeWithDeviceName(device_name)
        if not url:
            # Some error occurred, we're probably offline
            raise CoreOfflineException()
        self.out('Please open this url in your browser: {0}'.format(url))
        init_result = self.daemon_client.waitForAuthorization()
        if init_result == InitResult.OFFLINE:
            raise CoreOfflineException()
        elif init_result == InitResult.TIMEDOUT:
            raise TimeoutException()
        elif init_result != InitResult.AUTHORIZATION_OK:
            # TODO improve error handling
            assert False
        self.out('Your client has successfully been associated with your account.')

    @exceptions_handled
    def start(self):
        log.debug('CLIHandler.start()')
        try:
            # TODO test killing in the middle of each action
            while True:
                self._start_daemon()
                self._handle_cloud_home()
                self.daemon_client.startCore()
                init_result = self.daemon_client.init()
                if init_result == InitResult.OFFLINE:
                    raise CoreOfflineException()
                elif init_result == InitResult.AUTHORIZATION_REQUIRED:
                    self._handle_client_registration()
                elif init_result == InitResult.ROOT_FOLDER_MISSING:
                    cloud_home = self.ui_config.get('cloud_home')
                    self.out('Could not find your MEO Cloud\'s folder in path "{0}".'.format(cloud_home))
                    self.ui_config.unset('cloud_home')
                    with open(PURGEMETA_PATH, 'w'):
                        # touch
                        pass
                    self.stop(quiet=True)
                    continue
                elif init_result == InitResult.TIMEDOUT:
                    raise TimeoutException()
                elif init_result != InitResult.AUTHORIZATION_OK:
                    # TODO improve error handling
                    assert False
                break
            # TODO wait for sync start?
            self.out('MEO Cloud is ready to use.')
            return True
        except CoreOfflineException:
            self.out('It was not possible to establish a connection to the MEO Cloud servers.')
            self.out('Please check your connection, or if you\'re behind a proxy, '
                     'set it using the http_proxy environment variable or the proxy command.')
            self.stop()
        except AlreadyRunningException:
            self.out('Failed to start MEO Cloud.')
            self.out('MEO Cloud was running already.')
        except (socket.timeout, ListenerConnectionFailedException, EOFError, KeyboardInterrupt):
            self.out('Failed to start MEO Cloud.')
            self.stop(quiet=True)
            raise

    def stop(self, quiet=False):
        log.debug('CLIHandler.stop()')
        stopped = False

        pid = self._daemon_already_running()
        if pid:
            try:
                log.info('CLIHandler.stop: gracefull daemon shutdown')
                self.daemon_client.shutdown()
                stopped = True
                # Sleep a bit to give time for the daemon and the core
                # to gracefully shut themselves
                time.sleep(2)
            except (ListenerConnectionFailedException, socket.timeout):
                pass

            if not stopped or self._daemon_already_running():
                # Connection to daemon_client might have been lost
                # or the gracefull kill wasn't enough.
                # Will try to kill using pid
                log.info('CLIHandler.stop: forcefull daemon shutdown')
                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    # If we failed to kill it there's a good chance that the reason
                    # is that he's already dead
                    pass
                stopped = True

        pid = self._core_already_running()
        if pid:
            # Apparently we have a dangling core...
            # Kill it!
            log.info('CLIHandler.stop: forcefull core shutdown')
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                # If we failed to kill it there's a good chance that the reason
                # is that he's already dead
                pass
            stopped = True

        if not quiet:
            if stopped:
                self.out('MEO Cloud has been stopped.')
            else:
                self.out('MEO Cloud does not seem to be running.')
        return True

    @exceptions_handled
    @daemon_must_be_running
    def status(self):
        log.debug('CLIHandler.status()')
        status_result = self.daemon_client.status()
        status = status_result.status

        if status_result.persistentNotifs:
            for persistent_notif in status_result.persistentNotifs:
                self.out('WARNING: {0}'.format(persistent_notif))

        if status.totalQuota:
            percentage = float(status.usedQuota) / status.totalQuota
            used_quota_human_readable = human_readable_bytes(status.usedQuota)
            total_quota_human_readable = human_readable_bytes(status.totalQuota)
            self.out('Quota: {0:.2%} ({1} of {2})'.format(
                percentage, used_quota_human_readable, total_quota_human_readable))

        if status.state == State.READY:
            self.out('Status: IDLE')
        else:
            self.out('Status: {0}'.format(State._VALUES_TO_NAMES[status.state]))

        sync_status = status_result.syncStatus
        if sync_status:
            # TODO Handle sync_code
            log.debug('CLIHandler.status: sync_code: {0}'.format(sync_status.syncCode))
            if sync_status.pendingUploads:
                if sync_status.uploadRate:
                    self.out('Uploading {0} files, at {1} ({2} left)'.format(
                        sync_status.pendingUploads,
                        human_readable_bytes(sync_status.uploadRate, per_second=True),
                        human_readable_seconds(sync_status.uploadETASecs)
                    ))
                else:
                    self.out('Uploading {0} files'.format(sync_status.pendingUploads))
            if sync_status.pendingDownloads:
                if sync_status.downloadRate:
                    self.out('Downloading {0} files, at {1} ({2} left)'.format(
                        sync_status.pendingDownloads,
                        human_readable_bytes(sync_status.downloadRate, per_second=True),
                        human_readable_seconds(sync_status.downloadETASecs)
                    ))
                else:
                    self.out('Downloading {0} files'.format(sync_status.pendingDownloads))
            if sync_status.pendingIndexes:
                self.out('Indexing {0} files'.format(sync_status.pendingIndexes))
        return True

    @exceptions_handled
    @daemon_must_be_running
    def notifications(self, n_lines):
        log.debug('CLIHandler.notifications()')
        try:
            with open(NOTIFICATIONS_LOG_PATH, 'r') as f:
                lines = tail(f, n_lines)
        except IOError:
            lines = None
        if lines:
            self.out('\n'.join(lines))
        else:
            self.out('You have no notifications')
        return True

    @exceptions_handled
    @daemon_must_be_running
    def list_sync(self):
        log.debug('CLIHandler.list_sync()')
        ignored_directories = self.daemon_client.ignoredDirectories()
        if not ignored_directories:
            self.out('All your directories are being synchronized.')
        else:
            self.out('All directories are being synchronized except these:')
            self.out('\n'.join(ignored_directories))
        return True

    @exceptions_handled
    @daemon_must_be_running
    def add_sync(self, path):
        log.debug('CLIHandler.add_sync({0})'.format(path))
        if path == '__ALL__':
            self.daemon_client.setIgnoredDirectories([])
            self.out('Synchronization was resumed for every path whose synchronization was stopped.')
        else:
            orig_path = path
            normalized_path = path.rstrip('/')
            if normalized_path == '':
                self.out('"/" is the root of your MEO Cloud folder whose synchronization '
                         'cannot be stopped and thus does not need to be resumed.')
            else:
                normalized_path = self.test_or_add_leading_slash(normalized_path, orig_path)
                ignored_directories = self.daemon_client.ignoredDirectories()
                if normalized_path in ignored_directories:
                    if self.test_valid_path(normalized_path, orig_path, quiet=True):
                        self.out('"{0}" will now be added back to your MEO Cloud folder '
                                 'and its synchronization will resume.'.format(orig_path))
                    else:
                        self.out('"{0}" has been removed from the '
                                 'stopped synchronization list'.format(orig_path))
                    ignored_directories.remove(normalized_path)
                    self.daemon_client.setIgnoredDirectories(ignored_directories)
                elif self.test_valid_path(normalized_path, orig_path):
                    self.out('Nothing to do. "{0}" was already being synchronized.'.format(orig_path))
        return True

    @exceptions_handled
    @daemon_must_be_running
    def remove_sync(self, path, force):
        log.debug('CLIHandler.remove_sync({0})'.format(path))
        orig_path = path
        normalized_path = path.rstrip('/')
        if normalized_path == '':
            self.out('Cannot stop synchronizing the root of your MEO Cloud folder.')
        else:
            normalized_path = self.test_or_add_leading_slash(normalized_path, orig_path)
            ignored_directories = self.daemon_client.ignoredDirectories()
            if normalized_path in ignored_directories:
                self.out('Nothing to do. Synchronization of "{0}" was already stopped.'.format(orig_path))
            elif force or self.test_valid_path(normalized_path, orig_path):
                    ignored_directories.append(normalized_path)
                    self.daemon_client.setIgnoredDirectories(ignored_directories)
                    self.out('"{0}" was removed from the synced paths and will be removed '
                             'from your filesystem when syncing is done.'.format(orig_path))
        return True

    def test_or_add_leading_slash(self, normalized_path, orig_path):
        # No leading slash
        if not normalized_path.startswith('/'):
            self.out('Your path did not start with a slash (/).')
            yes = self.ask_yes_no('Did you mean {0}'.format('/' + orig_path))
            if yes:
                normalized_path = '/' + normalized_path
        return normalized_path

    def test_valid_path(self, normalized_path, orig_path, quiet=False):
        if normalized_path.startswith('/'):
            parent_dir = os.path.dirname(normalized_path)
        else:
            parent_dir = '/'
        remote_directories = self.daemon_client.remoteDirectoryListing(parent_dir).listing

        if remote_directories is None:
            if quiet:
                return True
            self.out('Could not contact the server to validate that path "{0}"'
                     ' is a valid path in your MEO Cloud folder.'.format(orig_path))
            return self.ask_yes_no('Do you want to continue?')
        # TODO handle remoteDirectoryListing statusCode
        if normalized_path not in remote_directories:
            if quiet:
                return False
            self.out('Path "{0}" is not a correct path in your MEO Cloud folder'.format(orig_path))
            if not remote_directories and parent_dir != '/':
                # Either the folder was empty or the parent folder was invalid.
                # Since there is no easy way of knowing what happened, we'll just list the examples for the root folder
                parent_dir = '/'
                remote_directories = self.daemon_client.remoteDirectoryListing(parent_dir).listing
            if remote_directories:
                self.out('Here are some examples of correct paths:')
                for correct_path in remote_directories[:20]:
                    self.out(correct_path)
            elif parent_dir == '/':
                self.out('You have no folders in MEO Cloud, which means there is no correct path.')
            else:
                assert False
            return False
        return True

    @exceptions_handled
    def proxy(self, proxy_url):
        log.debug('CLIHandler.proxy()')
        if proxy_url is None:
            current_proxy = get_proxy(self.ui_config)
            if current_proxy:
                self.out('Current Proxy: {0}'.format(current_proxy))
            else:
                self.out('No proxy in use.')
        else:
            if proxy_url == 'default':
                set_proxy(self.ui_config, None)
                self.out('Proxy settings reset.')
                current_proxy = get_proxy(self.ui_config)
                if current_proxy:
                    self.out('Current Proxy: {0} (from http_proxy or https_proxy environment variables)'.format(current_proxy))
            else:
                set_proxy(self.ui_config, proxy_url)
                self.out('Proxy was set to: {0}'.format(proxy_url))
            if self._daemon_already_running():
                self.daemon_client.networkSettingsChanged()
        return True

    @exceptions_handled
    def ratelimit(self, direction, limit):
        log.debug('CLIHandler.ratelimit()')
        download_limit, upload_limit = get_ratelimits(self.ui_config)
        if direction is not None:
            if limit > 1000000:
                self.out('Limit cannot exceed 1000000 KB/s (1 GB/s).')
                return False
            if direction == 'up':
                upload_limit = limit
            elif direction == 'down':
                download_limit = limit
            else:
                self.out('First parameter must be \'up\' or \'down\'.')
                return False
            set_ratelimits(self.ui_config, download_limit, upload_limit)
            if self._daemon_already_running():
                self.daemon_client.networkSettingsChanged()
        if upload_limit == 0:
            self.out('Upload limit: N/A')
        else:
            self.out('Upload limit: {0} KB/s'.format(upload_limit))
        if download_limit == 0:
            self.out('Download limit: N/A')
        else:
            self.out('Download limit: {0} KB/s'.format(download_limit))
        return True

    @exceptions_handled
    @daemon_must_be_running
    def pause(self):
        log.debug('CLIHandler.pause()')
        self.daemon_client.pause()
        self.out('MEO Cloud synchronization was stopped. Enter meocloud resume to restart sync.')
        return True
        # TODO Warn if already paused

    @exceptions_handled
    @daemon_must_be_running
    def resume(self):
        log.debug('CLIHandler.resume()')
        self.daemon_client.unpause()
        self.out('MEO Cloud synchronization was resumed.')
        return True
        # TODO Warn if already unpaused

    @exceptions_handled
    @check_daemon_version
    def version(self):
        log.debug('CLIHandler.version()')
        try:
            core_version = self.daemon_client.coreVersion()
        except ListenerConnectionFailedException:
            self.out('{0}'.format(VERSION))
        else:
            self.out('{0} (core version: {1})'.format(VERSION, core_version))
        return True

    @exceptions_handled
    @daemon_must_be_running
    def unlink(self):
        log.debug('CLIHandler.unlink()')
        # Make sure user wants to unlink
        really_unlink = self.ask_yes_no('Are you sure you want to unlink your account')

        # Actually unlink
        if really_unlink:
            unlink_success = self.daemon_client.unlink()
            if unlink_success:
                self.out('Successfully unlinked account.')
            else:
                self.out('No account to unlink.')
            self.stop()
        return True

    def ask(self, msg='', default=None, *args, **kwargs):
        if default:
            msg = msg + ' [{0}]? '.format(default)
        else:
            msg = msg + '? '
        self.out(msg, end='')
        answer = self.get_input()
        if not answer and default is not None:
            answer = default
        return answer

    def ask_yes_no(self, msg='', default_yes=False, *args, **kwargs):
        if default_yes:
            msg = msg + ' [n/Y]? '
            default = 'y'
        else:
            msg = msg + ' [N/y]? '
            default = 'n'
        while True:
            self.out(msg, end='')
            answer = self.get_input()
            if not answer:
                answer = default
            if answer.lower() == 'y':
                return True
            if answer.lower() == 'n':
                return False
            self.out('Did not recognize answer "{0}". Please answer again.'.format(answer))

    def get_input(self):
        if not sys.stdin.isatty():
            log.warning('CLI: Must get input but stdin is not a terminal.')
            self.out()
            self.out('ERROR: Must get input but stdin is not a terminal.')
            self.stop(quiet=True)
            self.out('Goodbye!')
            sys.exit(1)
        return input().strip()

    def out(self, msg='', *args, **kwargs):
        print_(msg, *args, **kwargs)
