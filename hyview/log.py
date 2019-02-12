import logging
from hyview.constants import LOGGING_LEVEL


logging.basicConfig()


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)
    return logger
