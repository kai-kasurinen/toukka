#

import os.path

from dogpile.cache import make_region
from xdg.BaseDirectory import save_cache_path


# FIXME: rename
region = make_region()


def configure():

    _cache_path = save_cache_path('toukka', 'dogpile')
    _cache_file = os.path.join(_cache_path, 'cache.dbm')

    config = {
        # local file
        'cache.local.backend': 'dogpile.cache.dbm',
        'cache.local.arguments.filename': _cache_file,
        'cache.local.expiration_time': 60*60*24,
        # local redis
        'cache.redis.backend': 'dogpile.cache.redis',
        'cache.redis.redis_expiration_time': 60*60*24*2,
        'cache.redis.expiration_time': 60*60*24
    }

    # region.configure_from_config(config, 'cache.local.')
    region.configure_from_config(config, 'cache.redis.')


# FIXME: removes
configure()

# END
