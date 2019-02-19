import logging
from hyview.constants import LOGGING_LEVEL


logging.basicConfig()


def get_logger(name):
    """
    Helper to get a logger that is configured at a top-level.

    Parameters
    ----------
    name : str

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)
    return logger
