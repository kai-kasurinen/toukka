#

import logging


def init_logging():

    logging.basicConfig(
        level=logging.INFO,
        # format='%(asctime)s %(name)s %(levelname)s %(message)s'
        # format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s'
        # format='%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s'
        format='%(asctime)s %(levelname)-8s %(name)s.%(funcName)s: %(message)s'
        )
    logging.captureWarnings(True)


def set_logging_level(level):
    logging.getLogger().setLevel(level)


# END
