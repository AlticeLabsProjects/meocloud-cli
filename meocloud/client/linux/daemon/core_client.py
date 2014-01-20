from meocloud.client.linux.settings import DAEMON_LISTENER_SOCKET_ADDRESS, LOGGER_NAME
from meocloud.client.linux.timeouts import CONNECTION_REQUIRED_TIMEOUT
from meocloud.client.linux.protocol.daemon_core import Core
from meocloud.client.linux.thrift_utils import ThriftClient, wrap_client_call

import logging
log = logging.getLogger(LOGGER_NAME)


class CoreClient(ThriftClient, Core.Iface):
    def __init__(self):
        super(CoreClient, self).__init__(DAEMON_LISTENER_SOCKET_ADDRESS, Core.Client)

    # I know you wanted to remove the parenthesis, but believe me, you don't
    @wrap_client_call()
    def currentStatus(self):
        return self.client.currentStatus()

    @wrap_client_call()
    def currentSyncStatus(self):
        return self.client.currentSyncStatus()

    @wrap_client_call()
    def recentlyChangedFilePaths(self):
        return self.client.recentlyChangedFilePaths()

    @wrap_client_call()
    def pause(self):
        return self.client.pause()

    @wrap_client_call()
    def unpause(self):
        return self.client.unpause()

    @wrap_client_call()
    def shutdown(self):
        return self.client.shutdown()

    @wrap_client_call(timeout=CONNECTION_REQUIRED_TIMEOUT)
    def authorizeWithDeviceName(self, deviceName):
        return self.client.authorizeWithDeviceName(deviceName)

    @wrap_client_call()
    def startSync(self, rootFolder):
        return self.client.startSync(rootFolder)

    @wrap_client_call()
    def unlink(self, account):
        return self.client.unlink(account)

    @wrap_client_call()
    def notify(self, note):
        return self.client.notify(note)

    @wrap_client_call()
    def networkSettingsChanged(self, settings):
        return self.client.networkSettingsChanged(settings)

    @wrap_client_call()
    def requestRemoteDirectoryListing(self, path):
        return self.client.requestRemoteDirectoryListing(path)

    @wrap_client_call()
    def ignoredDirectories(self):
        return self.client.ignoredDirectories()

    @wrap_client_call()
    def setIgnoredDirectories(self, paths):
        return self.client.setIgnoredDirectories(paths)

    @wrap_client_call()
    def webLoginURL(self):
        return self.client.webLoginURL()

    @wrap_client_call()
    def ping(self):
        return self.client.ping()

    @wrap_client_call()
    def version(self):
        return self.client.version()
