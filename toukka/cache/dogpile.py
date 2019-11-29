#

import os.path

from dogpile.cache import make_region
from xdg.BaseDirectory import save_cache_path


null = make_region()
memory = make_region()
local = make_region()
redis = make_region()
mongo = make_region()


def configure():

    _cache_file = os.path.join(save_cache_path('toukka', 'dogpile'), 'local.dbm')

    config = {
        # null
        'cache.null.backend': 'dogpile.cache.null',
        # memory
        'cache.memory.backend': 'dogpile.cache.memory_pickle',
        # local file
        'cache.local.backend': 'dogpile.cache.dbm',
        'cache.local.expiration_time': 60*60*24,
        'cache.local.arguments.filename': _cache_file,
        # local redis
        'cache.redis.backend': 'dogpile.cache.redis',
        'cache.redis.expiration_time': 60*60*24,
        'cache.redis.arguments.url': 'redis://?db=10',
        # NOTE: This should be larger than dogpile’s cache expiration.
        'cache.redis.arguments.redis_expiration_time': 60*60*24,
        # NOTE: Use this when multiple processes will be talking to the same redis instance
        'cache.redis.arguments.distributed_lock': True,
        # mongo
        'cache.mongo.backend': 'mongo',
        'cache.mongo.expiration_time': 60*60*24,
        'cache.mongo.arguments.db': False,
        'cache.mongo.arguments.uri': 'localhost',
        'cache.mongo.arguments.db_name': 'toukka',
    }

    null.configure_from_config(config, 'cache.null.')
    memory.configure_from_config(config, 'cache.memory.')
    local.configure_from_config(config, 'cache.local.')
    redis.configure_from_config(config, 'cache.redis.')
    mongo.configure_from_config(config, 'cache.mongo.')


# FIXME: removes
configure()

# END
