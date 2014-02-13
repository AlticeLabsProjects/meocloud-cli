# Thrift related imports
from meocloud.client.linux.protocol.daemon_ui.ttypes import InitResult, StatusResult, RemoteDirectoryListingResult, SyncStatus
from meocloud.client.linux.protocol.daemon_core.ttypes import State
from meocloud.client.linux.protocol.daemon_ui import UI
from meocloud.client.linux.thrift_utils import ThriftListener

# Application specific imports
from meocloud.client.linux.settings import LOGGER_NAME, VERSION
from meocloud.client.linux.timeouts import CONNECTION_REQUIRED_TIMEOUT, USER_ACTION_REQUIRED_TIMEOUT
from meocloud.client.linux.daemon.communication import Events, AsyncResults, DaemonState
from meocloud.client.linux.daemon import api
from meocloud.client.linux.utils import get_sync_code, dict_from_slots_obj

# Logging
import logging
log = logging.getLogger(LOGGER_NAME)


class UIListener(ThriftListener):
    def __init__(self, socket, core_client, ui_config, notifs_handler):
        handler = UIListenerHandler(core_client, ui_config, notifs_handler)
        processor = UI.Processor(handler)
        super(UIListener, self).__init__('UIListener', socket, processor)


class UIListenerHandler(UI.Iface):
    def __init__(self, core_client, ui_config, notifs_handler):
        super(UIListenerHandler, self).__init__()
        self.core_client = core_client
        self.ui_config = ui_config
        self.notifs_handler = notifs_handler

    ### THRIFT METHODS ###

    def waitForAuthorization(self):
        return self.init(timeout=USER_ACTION_REQUIRED_TIMEOUT)

    def init(self, timeout=CONNECTION_REQUIRED_TIMEOUT):
        log.debug('UIListener.init() <<<<')
        Events.state_changed.wait(timeout=timeout)
        if Events.state_changed.is_set():
            Events.state_changed.clear()
            log.debug('UIListener.init: State has changed, current state: {0}'.format(DaemonState.current))
            if DaemonState.current == DaemonState.AUTHORIZATION_REQUIRED:
                return InitResult.AUTHORIZATION_REQUIRED
            elif DaemonState.current == DaemonState.OFFLINE:
                return InitResult.OFFLINE
            elif DaemonState.current == DaemonState.AUTHORIZATION_OK:
                return InitResult.AUTHORIZATION_OK
            elif DaemonState.current == DaemonState.ROOT_FOLDER_MISSING:
                return InitResult.ROOT_FOLDER_MISSING
            # TODO Improve error handling
            assert False
        else:
            log.warning('UIListener.init: Timed-out while waiting for state change')
            Events.shutdown_required.set()
            return InitResult.TIMEDOUT

    def startCore(self):
        log.info('UIListener.startCore() <<<<')
        Events.core_start_ready.set()

    def authorizeWithDeviceName(self, device_name):
        log.debug('UIListener.authorizeWithDeviceName({0}) <<<<'.format(device_name))
        url = self.core_client.authorizeWithDeviceName(device_name)
        return url

    def status(self):
        log.debug('UIListener.status() <<<<')
        status_result = StatusResult()
        status = self.core_client.currentStatus()
        if status.state == State.SYNCING:
            sync_status = self.core_client.currentSyncStatus()
            sync_status_dict = dict_from_slots_obj(sync_status)
            sync_status_dict['syncCode'] = get_sync_code(status.statusCode)
            status_result.syncStatus = SyncStatus(**sync_status_dict)
        status_result.status = status
        status_result.persistentNotifs = self.notifs_handler.get_persistent_notifs()
        return status_result

    def recentlyChangedFilePaths(self):
        log.debug('UIListener.recentlyChangedFilePaths() <<<<')
        pass

    def pause(self):
        log.debug('UIListener.pause() <<<<')
        self.core_client.pause()

    def unpause(self):
        log.debug('UIListener.unpause() <<<<')
        self.core_client.unpause()

    def shutdown(self):
        log.debug('UIListener.shutdown() <<<<')
        Events.shutdown_required.set()

    def unlink(self):
        log.debug('UIListener.unlink() <<<<')
        return api.unlink(self.core_client, self.ui_config)

    def networkSettingsChanged(self):
        log.debug('UIListener.networkSettingsChanged() <<<<')
        self.core_client.networkSettingsChanged(api.get_network_settings(self.ui_config))

    def remoteDirectoryListing(self, path):
        log.debug('UIListener.requestRemoteDirectoryListing({0}) <<<<'.format(path))
        AsyncResults.remote_directory_listing.create()
        self.core_client.requestRemoteDirectoryListing(path)
        args = AsyncResults.remote_directory_listing.get(timeout=CONNECTION_REQUIRED_TIMEOUT)
        if args is None:
            return RemoteDirectoryListingResult()
        result = RemoteDirectoryListingResult()
        result.statusCode = args['statusCode']
        result.path = args['path']
        result.listing = args['listing']
        return result

    def ignoredDirectories(self):
        log.debug('UIListener.ignoredDirectories() <<<<')
        return self.core_client.ignoredDirectories()

    def setIgnoredDirectories(self, paths):
        log.debug('UIListener.setIgnoredDirectories({0}) <<<<'.format(paths))
        self.core_client.setIgnoredDirectories(paths)

    def webLoginURL(self):
        log.debug('UIListener.webLoginURL() <<<<')
        pass

    def ping(self):
        log.debug('UIListener.ping() <<<<')
        return True

    def version(self):
        log.debug('UIListener.version() <<<<')
        return VERSION

    def coreVersion(self):
        log.debug('UIListener.coreVersion() <<<<')
        return self.core_client.version()
