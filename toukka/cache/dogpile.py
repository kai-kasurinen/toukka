#

import os.path

from dogpile.cache import make_region
from xdg.BaseDirectory import save_cache_path


null = make_region()
memory = make_region()
local = make_region()
redis = make_region()


def configure():

    _cache_file = os.path.join(save_cache_path('toukka', 'dogpile'), 'local.dbm')

    config = {
        # null
        'cache.null.backend': 'dogpile.cache.null',
        # memory
        'cache.memory.backend': 'dogpile.cache.memory_pickle',
        # local file
        'cache.local.backend': 'dogpile.cache.dbm',
        'cache.local.arguments.filename': _cache_file,
        'cache.local.expiration_time': 60*60*24,
        # local redis
        'cache.redis.backend': 'dogpile.cache.redis',
        'cache.redis.url': 'redis://',
        'cache.redis.expiration_time': 60*60*24,
        # NOTE: This should be larger than dogpile’s cache expiration.
        'cache.redis.redis_expiration_time': 60*60*24,
        # NOTE: Use this when multiple processes will be talking to the same redis instance
        'cache.redis.distributed_lock': True
    }

    null.configure_from_config(config, 'cache.null.')
    memory.configure_from_config(config, 'cache.memory.')
    local.configure_from_config(config, 'cache.local.')
    redis.configure_from_config(config, 'cache.redis.')


# FIXME: removes
configure()

# END
