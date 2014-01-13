import datetime

from meocloud.client.linux.daemon import codes
from meocloud.client.linux import strings

from meocloud.client.linux.settings import LOGGER_NAME, NOTIFICATIONS_LOG_PATH

# Logging
import logging
log = logging.getLogger(LOGGER_NAME)


class NotificationsHandler(object):
    def __init__(self):
        self.persistent_notifs = {}

    def handle(self, notification):
        log.debug('NotificationsHandler.handle({0}) <<<<'.format(notification))
        if notification.type == codes.USER_NOTIFY_TYPE_RESET:
            if notification.code in self.persistent_notifs:
                del self.persistent_notifs[notification.code]
        else:
            string_key = '{0}_description'.format(notification.code)
            format_string = strings.NOTIFICATIONS['en'][string_key]
            notif_string = format_string.format(*notification.parameters)
            if notification.type & codes.USER_NOTIFY_TYPE_MASK_PERSISTENT:
                self.persistent_notifs[notification.code] = notif_string
            else:
                time_str = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                with open(NOTIFICATIONS_LOG_PATH, 'a') as f:
                    f.write('{0} --> {1}\n'.format(time_str, notif_string))

    def get_persistent_notifs(self):
        log.debug('NotificationsHandler.get_persistent_notifs() <<<<')
        return self.persistent_notifs.values()
