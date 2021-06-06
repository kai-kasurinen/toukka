

import os
import logging

from xdg.BaseDirectory import save_cache_path


def set_logging_file():
    file = os.path.join(save_cache_path('toukka'), 'toukka.log')
    file_handler = logging.FileHandler(file)
    # FIXME: modify
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    # FIXME: Not working?
    file_handler.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(file_handler)
