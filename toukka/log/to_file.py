

import os
import logging

from xdg.BaseDirectory import save_cache_path

def set_logging_file():
    file = os.path.join(save_cache_path('toukka'), 'toukka.log')
    fh = logging.FileHandler(file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    # FIXME: Not working?
    fh.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(fh)
