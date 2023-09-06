import logging
from logging import getLogger, INFO, DEBUG


def get_logger(debug=False):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s - %(message)s",
    )
    logger = getLogger(__name__)
    logger.setLevel(DEBUG if debug else INFO)
    return logger
