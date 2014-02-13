import urlparse
from meocloud.client.linux.protocol.daemon_core.ttypes import NetworkSettings, Account
from meocloud.client.linux.settings import RC4_KEY
from meocloud.client.linux.daemon import rc4
from meocloud.client.linux.utils import get_network_settings


def unlink(core_client, ui_config):
    account_dict = ui_config.get('account')
    if account_dict:
        if 'clientID' in account_dict:
            account_dict['clientID'] = rc4.decrypt(account_dict['clientID'], RC4_KEY)
        if 'authKey' in account_dict:
            account_dict['authKey'] = rc4.decrypt(account_dict['authKey'], RC4_KEY)
        account = Account(**account_dict)
        ui_config.unset('account')
        ui_config.unset('cloud_home')
        core_client.unlink(account)
        return True
    return False


def get_network_settings_for_core(ui_config):
    network_settings = NetworkSettings()
    proxy_url = get_network_settings(ui_config)
    if proxy_url:
        try:
            parsed = urlparse.urlparse(proxy_url)
        except Exception:
            # Something went wrong while trying to parse proxy_url
            # Ignore and just don't use any proxy
            pass
        else:
            if parsed.hostname:
                network_settings.proxyAddress = parsed.hostname
                network_settings.proxyType = 'http'
                network_settings.proxyPort = parsed.port or 3128
                network_settings.proxyUser = parsed.user if hasattr(parsed, 'user') else ''
                network_settings.proxyPassword = parsed.password if hasattr(parsed, 'password') else ''
                network_settings.uploadBandwidth = 0
                network_settings.downloadBandwidth = 0
    return network_settings
