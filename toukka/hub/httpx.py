#

import httpx
import httpx_cache

import xdg.BaseDirectory

from toukka.adapted.httpx_cache_diskcache import FanOutCacheAdapter


def get_diskcache():
    dir = xdg.BaseDirectory.save_cache_path('toukka', 'httpx_cache_diskcache')

    cache = FanOutCacheAdapter(
        dir,
        timeout=10,
        statistics=True,
        size_limit=2**31,        # 2147483648
        disk_min_file_size=2**20)  # 1048576

    return cache


def get_filecache():
    # by default the cached files will be saved in $HOME/.cache/httpx-cache folder.
    cache = httpx_cache.FileCache()
    return cache


def get_client(client_type='cache'):
    if client_type == 'plain':
        return httpx.Client()
    elif client_type == 'cache':

        # cache = get_filecache()
        cache = get_diskcache()

        transport_http = httpx.HTTPTransport(retries=3)
        transport_cache = httpx_cache.CacheControlTransport(cache=cache, transport=transport_http)

        return httpx.Client(transport=transport_cache, http2=True, timeout=30.0)

# END
