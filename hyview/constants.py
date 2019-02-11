import os
import logging


SERVER_HOST = os.environ.get('HYVIEW_HOST', '127.0.0.1')
SERVER_PORT = os.environ.get('HYVIEW_SERVER_PORT', '4241')
BUILD_PORT = os.environ.get('HYVIEW_BUILD_PORT', '4242')

CACHE_DIR = os.environ.get('HYVIEW_CACHE_DIR', '/tmp/hyview')

LOGGING_LEVEL = logging._nameToLevel.get(
    os.environ.get('HYVIEW_LOGGING_LEVEL', 'DEBUG'), logging.DEBUG)
