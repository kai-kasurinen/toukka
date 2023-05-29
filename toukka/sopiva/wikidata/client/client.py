#

import wikidata
import wikidata.client
import diskcache
import xdg.BaseDirectory

def get_cache():
    dir = xdg.BaseDirectory.save_cache_path('toukka', 'wikidata_diskcache')
    cache = diskcache.FanoutCache(
        dir,
        timeout=10,
        statistics=True,
        size_limit=2**31,          # 2147483648
        disk_min_file_size=2**20)  # 1048576
    return cache

def get_wikidata_client():
        # cache_policy = wikidata.cache.MemoryCachePolicy(max_size=1024)
        cache_policy = wikidata.cache.ProxyCachePolicy(get_cache(), timeout=86400, property_timeout=604800)
        wikidata_client = wikidata.client.Client(cache_policy=cache_policy)
        return wikidata_client

