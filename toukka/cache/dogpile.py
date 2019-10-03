#

import os.path

from dogpile.cache import make_region
from xdg.BaseDirectory import save_cache_path


_cache_path = save_cache_path('toukka', 'dogpile')
_cache_file = os.path.join(_cache_path, 'cache.dbm')


region = make_region().configure(
    'dogpile.cache.dbm',
    expiration_time=86400,
    arguments={
        'filename': _cache_file
    }
)


# END
