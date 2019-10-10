#

import logging

# TODO:  https://pythonhosted.org/Autologging/examples-separate.html
# import autologging


def init_logging():
    # FIXME: fix format
    logging.basicConfig(
        level=logging.INFO,
        # format='%(asctime)s %(name)s %(levelname)s %(message)s'
        format='%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s'
        )
    logging.captureWarnings(True)


def set_logging_level(level):
    logging.getLogger().setLevel(level)


# END
