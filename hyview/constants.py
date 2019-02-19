import os
import logging


HOST = os.environ.get('HYVIEW_HOST', '127.0.0.1')
# Used by the server that Houdini client(s) talks to.
PORT = os.environ.get('HYVIEW_PORT', '4242')
# Used by the server running within Houdini.
APP_PORT = os.environ.get('HYVIEW_APP_PORT', '4241')

# Directory to use for cachine results.
CACHE_DIR = os.environ.get('HYVIEW_CACHE_DIR', '/tmp/hyview')

_LOGGING_LOOKUP = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}

LOGGING_LEVEL = _LOGGING_LOOKUP.get(
    os.environ.get('HYVIEW_LOGGING_LEVEL', 'DEBUG'), logging.DEBUG)
