#

import diskcache

from dogpile.cache.api import CacheBackend, NO_VALUE
from dogpile.cache import register_backend

class FanoutCacheBackend(CacheBackend):
    def __init__(self, arguments):
        
        directory = arguments.get('directory')

        if directory is None:
            raise Exception()

        # seconds, month
        self.default_expire = 60*60*24*30

        self.cache = diskcache.FanoutCache(
            directory,
            timeout=10,
            statistics=True,
            shards=16,                 # default 8
            size_limit=2**31*2,        # 2147483648 * 2
            disk_min_file_size=2**20)  # 1048576

    def get(self, key):
        return self.cache.get(key, default=NO_VALUE)

    def set(self, key, value):
        self.cache.set(key, value, expire=self.default_expire)

    def delete(self, key):
        self.cache.pop(key)



register_backend('fanout', "toukka.adapted.dogpile_diskcache_backend", "FanoutCacheBackend")
