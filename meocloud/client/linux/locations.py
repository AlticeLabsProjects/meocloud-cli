import os

from meocloud.client.linux.settings import CONFIG_PATH, UI_CONFIG_PATH


def create_required_directories():
    create_required_directory(CONFIG_PATH)
    create_required_directory(UI_CONFIG_PATH)


def create_required_directory(directory):
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise RuntimeError('Path ({0}) already exists and is not a directory.'.format(directory))
    else:
        os.mkdir(directory)
