DEFAULT_TIMEOUT = 3
CONNECTION_REQUIRED_TIMEOUT = 15
# This takes as long as the user takes to authorize in the browser
# so we must wait a long while...
USER_ACTION_REQUIRED_TIMEOUT = 1200

def increase_timeouts(increment):
    global DEFAULT_TIMEOUT
    global CONNECTION_REQUIRED_TIMEOUT
    global USER_ACTION_REQUIRED_TIMEOUT
    DEFAULT_TIMEOUT += increment
    CONNECTION_REQUIRED_TIMEOUT += increment
    USER_ACTION_REQUIRED_TIMEOUT += increment
