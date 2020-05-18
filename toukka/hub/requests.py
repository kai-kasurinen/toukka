#

import logging
import requests
import requests.adapters
import cachecontrol
import cachecontrol.caches
import redis
import xdg.BaseDirectory

from urllib3.util.retry import Retry
from toukka.adapted.retry import RetryA

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


def get_cached_session(cache_type='redis') -> requests.Session:
    session = requests.Session()
    retry = get_retry()
    if cache_type == 'redis':
        cache = get_rediscache()
    elif cache_type == 'file':
        cache = get_filecache()
    else:
        raise Exception(f'not supported cache_type: {cache_type}')
    adapter = cachecontrol.CacheControlAdapter(cache, max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# END
