import sys
import os


def test_already_running(pid_path, proc_name):
    try:
        with open(pid_path) as f:
            pid = int(f.read())
        with open('/proc/{0}/cmdline'.format(pid)) as f:
            if proc_name in f.read():
                assert pid != 0
                return pid
    except Exception:
        # Either the application is not running or we have no way
        # to find it, so assume it is not running.
        pass
    return False


def get_error_code(status_code):
    # most significant byte
    return status_code >> 24


def get_sync_code(status_code):
    # least significant byte
    return status_code & 0xff


def tail(f, window=20):
    """
    Returns the last `window` lines of file `f` as a list.
    """
    if window == 0:
        return []
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window + 1
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if bytes - BUFSIZ > 0:
            # Seek back one whole BUFSIZ
            f.seek(block * BUFSIZ, 2)
            # read BUFFER
            data.insert(0, f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0, 0)
            # only read what was not read
            data.insert(0, f.read(bytes))
        linesFound = data[0].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return ''.join(data).splitlines()[-window:]


def dict_from_slots_obj(obj):
    slots = obj.__slots__
    attr_dict = {}
    for slot in slots:
        attr_dict[slot] = getattr(obj, slot)
    return attr_dict


def get_own_dir(own_filename):
    if getattr(sys, "frozen", False):
        own_path = sys.executable
    else:
        own_path = os.path.join(os.getcwd(), own_filename)
    return os.path.dirname(own_path)


def get_proxy(ui_config):
    proxy_url = ui_config.get('proxy_url')
    if proxy_url is None:
        proxy_url = os.getenv('http_proxy') or os.getenv('https_proxy')
    return proxy_url


def set_proxy(ui_config, proxy_url):
    set_config_value(ui_config, 'proxy_url', proxy_url)


def get_ratelimits(ui_config):
    download_limit = ui_config.get('download_limit') or 0
    upload_limit = ui_config.get('upload_limit') or 0
    return download_limit, upload_limit


def set_ratelimits(ui_config, download_limit, upload_limit):
    set_config_value(ui_config, 'download_limit', download_limit)
    set_config_value(ui_config, 'upload_limit', upload_limit)


def set_config_value(ui_config, key, value):
    if value is None:
        ui_config.unset(key)
    else:
        ui_config.set(key, value)
