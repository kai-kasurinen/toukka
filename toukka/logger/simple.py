#

import logging
import autologging

# TODO:  https://pythonhosted.org/Autologging/examples-separate.html


def init_logging():
    # FIXME: fix format
    logging.basicConfig(
        level=logging.INFO,
        #format='%(asctime)s %(name)s %(levelname)s %(message)s'
        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s'
        # format='%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s'
        )
    logging.captureWarnings(True)


def set_logging_level(level):
    logging.getLogger().setLevel(level)


def set_logging_level_to_trace():
    set_logging_level(autologging.TRACE)

# END
