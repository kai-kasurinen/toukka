#

import os.path

from dogpile.cache import make_region
from xdg.BaseDirectory import save_cache_path


region_null = make_region()
region_memory = make_region()
region_local = make_region()
region_spotify = make_region()
#region_redis = make_region()
#region_mongo = make_region()


def configure():

    _local_cache_file = os.path.join(save_cache_path('toukka', 'dogpile'), 'local.dbm')
    _spotify_cache_file = os.path.join(save_cache_path('toukka', 'dogpile'), 'spotify.dbm')

    config = {
        # null
        'cache.null.backend': 'dogpile.cache.null',
        # memory
        'cache.memory.backend': 'dogpile.cache.memory_pickle',
        # local file
        'cache.local.backend': 'dogpile.cache.dbm',
        'cache.local.expiration_time': 60*60*24,
        'cache.local.arguments.filename': _local_cache_file,
        # spotify, local file
        'cache.spotify.backend': 'dogpile.cache.dbm',
        'cache.spotify.expiration_time': 60*60*24*30,
        'cache.spotify.arguments.filename': _spotify_cache_file,
        # local redis
        'cache.redis.backend': 'dogpile.cache.redis',
        'cache.redis.expiration_time': 60*60*24,
        'cache.redis.arguments.url': 'redis://?db=10',
        # NOTE: This should be larger than dogpile’s cache expiration.
        'cache.redis.arguments.redis_expiration_time': 60*60*24,
        # NOTE: Use this when multiple processes will be talking to the same redis instance
        'cache.redis.arguments.distributed_lock': True,
        # NOTE: should be set to False when distributed_lock is True
        'cache.redis.arguments.thread_local_lock': False,
        # mongo
        'cache.mongo.backend': 'mongo',
        'cache.mongo.expiration_time': 60*60*24,
        'cache.mongo.arguments.db': False,
        'cache.mongo.arguments.uri': 'localhost',
        'cache.mongo.arguments.db_name': 'toukka',
    }

    region_null.configure_from_config(config, 'cache.null.')
    region_memory.configure_from_config(config, 'cache.memory.')
    region_local.configure_from_config(config, 'cache.local.')
    region_spotify.configure_from_config(config, 'cache.spotify.')
    #region_redis.configure_from_config(config, 'cache.redis.')
    #mongo.configure_from_config(config, 'cache.mongo.')


# FIXME: removes
configure()

# END
