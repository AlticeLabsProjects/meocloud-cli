from meocloud.client.linux.settings import UI_LISTENER_SOCKET_ADDRESS, LOGGER_NAME
from meocloud.client.linux.timeouts import CONNECTION_REQUIRED_TIMEOUT, USER_ACTION_REQUIRED_TIMEOUT
from meocloud.client.linux.protocol.daemon_ui import UI
from meocloud.client.linux.thrift_utils import ThriftClient, wrap_client_call

import logging
log = logging.getLogger(LOGGER_NAME)


class DaemonClient(ThriftClient, UI.Iface):
    def __init__(self):
        super(DaemonClient, self).__init__(UI_LISTENER_SOCKET_ADDRESS, UI.Client)

    @wrap_client_call(timeout=CONNECTION_REQUIRED_TIMEOUT)
    def init(self):
        return self.client.init()

    @wrap_client_call(timeout=USER_ACTION_REQUIRED_TIMEOUT)
    def waitForAuthorization(self):
        return self.client.waitForAuthorization()

    @wrap_client_call(timeout=CONNECTION_REQUIRED_TIMEOUT)
    def authorizeWithDeviceName(self, deviceName):
        return self.client.authorizeWithDeviceName(deviceName)

    # I know you wanted to remove the parenthesis, but believe me, you don't
    @wrap_client_call()
    def getCloudHome(self):
        return self.client.getCloudHome()

    @wrap_client_call()
    def setCloudHome(self, cloudHome, forceCreate=False, forceMerge=False, forceRelative=False):
        return self.client.setCloudHome(cloudHome, forceCreate, forceMerge, forceRelative)

    @wrap_client_call()
    def clearCloudHome(self):
        return self.client.clearCloudHome()

    @wrap_client_call()
    def startCore(self):
        return self.client.startCore()

    @wrap_client_call()
    def status(self):
        return self.client.status()

    @wrap_client_call()
    def recentlyChangedFilePaths(self):
        return self.client.recentlyChangedFilePaths()

    @wrap_client_call()
    def pause(self):
        return self.client.pause()

    @wrap_client_call()
    def unpause(self):
        return self.client.unpause()

    @wrap_client_call(timeout=1)
    def shutdown(self):
        return self.client.shutdown()

    @wrap_client_call()
    def unlink(self):
        return self.client.unlink()

    @wrap_client_call()
    def networkSettingsChanged(self):
        return self.client.networkSettingsChanged()

    @wrap_client_call(timeout=CONNECTION_REQUIRED_TIMEOUT)
    def remoteDirectoryListing(self, path):
        return self.client.remoteDirectoryListing(path)

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

    @wrap_client_call(max_retries=6, sleep_time=0.1)
    def attemptFirstConnection(self):
        return self.client.ping()

    @wrap_client_call()
    def version(self):
        return self.client.version()

    @wrap_client_call()
    def coreVersion(self):
        return self.client.coreVersion()
