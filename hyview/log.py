import logging
from hyview.constants import LOGGING_LEVEL


logging.basicConfig()


def get(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)
    return logger
