#

import httpx
import httpx_cache

import xdg.BaseDirectory

from toukka.adapted.httpx_cache_diskcache import FanOutCacheAdapter


def get_diskcache():
    dir = xdg.BaseDirectory.save_cache_path('toukka', 'httpx_cache_diskcache')

    cache = FanOutCacheAdapter(dir,
                               timeout=10,
                               statistics=True,
                               disk_min_file_size=2**19)  # 524288
    return cache


def get_filecache():
    return httpx_cache.FileCache()


def get_client(client_type='cache'):
    if client_type == 'plain':
        return httpx.Client()
    elif client_type == 'cache':

        # by default the cached files will be saved in $HOME/.cache/httpx-cache folder.
        # cache = get_filecache()
        cache = get_diskcache()

        # transport = CacheControlTransport()
        transport = httpx_cache.CacheControlTransport(cache=cache)

        return httpx.Client(transport=transport)

# END
