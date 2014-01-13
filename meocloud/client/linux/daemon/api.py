from meocloud.client.linux.protocol.daemon_core.ttypes import Account
from meocloud.client.linux.settings import RC4_KEY
from meocloud.client.linux.daemon import rc4


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
