#

import requests
import requests.adapters
import urllib3.util.retry
import cachecontrol
import cachecontrol.caches
import redis
import xdg.BaseDirectory


def get_retry():
    retry = urllib3.util.retry.Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503))
    return retry


def get_session():
    session = requests.Session()
    retry = get_retry()
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_rediscache():
    redis_ = redis.Redis.from_url('redis://?db=15')
    cache = cachecontrol.caches.RedisCache(redis_)
    return cache


def get_filecache():
    path = xdg.BaseDirectory.save_cache_path('toukka', 'cachecontrol')
    cache = cachecontrol.caches.FileCache(path)
    return cache


def get_cached_session():
    session = requests.Session()
    retry = get_retry()
    cache = get_rediscache()
    adapter = cachecontrol.CacheControlAdapter(cache, max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# END
