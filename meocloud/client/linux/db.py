import yaml
from meocloud.client.linux.settings import UI_CONFIG_DB_FILE, LOGGER_NAME

# Logging
import logging
log = logging.getLogger(LOGGER_NAME)


# Hack to get yaml.safe_load to return all strings as str, instead of some as str
# and others as unicode
def construct_python_str(self, node):
    return self.construct_scalar(node).encode('utf-8')
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_python_str)


class UIConfig(object):

    def __init__(self):
        pass

    def load(self):
        try:
            with open(UI_CONFIG_DB_FILE) as f:
                data = yaml.safe_load(f)
        except (IOError, yaml.YAMLError):
            log.info('UIConfig.load(): Could not load data from file.')
            data = {}
        if data is None:
            data = {}
        return data

    def save(self, data):
        with open(UI_CONFIG_DB_FILE, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)

    def get(self, key):
        log.debug('UIConfig.get({0})'.format(key))
        data = self.load()
        try:
            return data[key]
        except KeyError:
            return None

    def set(self, key, value):
        log.debug('UIConfig.set({0}, {1})'.format(key, value))
        data = self.load()
        data[key] = value
        self.save(data)

    def unset(self, key):
        log.debug('UIConfig.unset({0})'.format(key))
        data = self.load()
        try:
            del data[key]
        except KeyError:
            pass
        self.save(data)
