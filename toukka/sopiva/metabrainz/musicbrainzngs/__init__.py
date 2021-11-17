#

import warnings

from musicbrainzngs import *


set_useragent('toukka', '0.0.0')

with warnings.catch_warnings(record=True):
    set_format('json')

# END
