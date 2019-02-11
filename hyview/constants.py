import os
import logging


HOST = os.environ.get('HYVIEW_HOST', '127.0.0.1')
PORT = os.environ.get('HYVIEW_PORT', '4242')
APP_PORT = os.environ.get('HYVIEW_APP_PORT', '4241')

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
