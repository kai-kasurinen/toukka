#

import logging


def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s %(message)s')
    logging.captureWarnings(True)


def set_logging_level(level):
    logging.getLogger().setLevel(level)


# END
