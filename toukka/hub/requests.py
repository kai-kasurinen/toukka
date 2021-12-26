#

import os
import logging
import requests
import requests.adapters
import cachecontrol
import cachecontrol.caches
# import cachecontrol_sqlite

import redis
import xdg.BaseDirectory

# import diskcache

from urllib3.util.retry import Retry
from toukka.adapted.urllib3_retry import RetryA
from toukka.adapted.cachecontrol_diskcache import FanOutCacheAdapter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_retry() -> Retry:
    logging.getLogger('urllib3.util.retry').setLevel(logging.DEBUG)
    #
    # RETRY_AFTER_STATUS_CODES = frozenset([413, 429, 503]
    # By default, we only retry on methods which are considered to be idempotent
    # (multiple requests with the same parameters end with the same state)
    # DEFAULT_METHOD_WHITELIST = frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'])
    #
    #
    default_method_whitelist = list(Retry.DEFAULT_METHOD_WHITELIST)
    retry = RetryA(
        total=4,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        method_whitelist=default_method_whitelist+['POST'])
    return retry


def get_session() -> requests.Session:
    session = requests.Session()
    retry = get_retry()
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_rediscache() -> cachecontrol.caches.RedisCache:
    redis_ = redis.Redis.from_url('redis://?db=15')
    cache = cachecontrol.caches.RedisCache(redis_)
    return cache


def get_filecache() -> cachecontrol.caches.FileCache:
    path = xdg.BaseDirectory.save_cache_path('toukka', 'cachecontrol')
    cache = cachecontrol.caches.FileCache(path)
    return cache


# def get_sqlitecache():
#    dir = xdg.BaseDirectory.save_cache_path('toukka')
#    file = os.path.join(dir, 'cachecontrol.db')
#    cache = cachecontrol_sqlite.SQLiteCache(file)
#     return cache


def get_diskcache():
    dir = xdg.BaseDirectory.save_cache_path('toukka', 'cachecontrol_diskcache')

    cache = FanOutCacheAdapter(dir,
                               timeout=10,
                               statistics=True,
                               disk_min_file_size=2**19)  # 524288
    return cache


def get_cached_session(cache_type='diskcache') -> requests.Session:
    session = requests.Session()
    retry = get_retry()
    if cache_type == 'redis':
        cache = get_rediscache()
    elif cache_type == 'file':
        cache = get_filecache()
    # elif cache_type == 'sqlite':
    #     cache = get_sqlitecache()
    elif cache_type == 'diskcache':
        cache = get_diskcache()
    else:
        raise Exception(f'not supported cache_type: {cache_type}')
    adapter = cachecontrol.CacheControlAdapter(cache, max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# END
