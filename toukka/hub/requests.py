#

import requests
import requests.adapters
import urllib3.util.retry
import cachecontrol
import cachecontrol.caches
import redis


# NOTE: not tested =)
def get_session():
    session = requests.Session()
    retry = urllib3.util.retry.Retry(total=3)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_session_cached():
    # TODO: add file_cache support
    redis_connection_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    redis_ = redis.Redis(connection_pool=redis_connection_pool)
    session = requests.Session()
    retry = urllib3.util.retry.Retry(total=3)
    cache = cachecontrol.caches.RedisCache(redis_)
    adapter = cachecontrol.CacheControlAdapter(cache, max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# END
