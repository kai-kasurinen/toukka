#

import logging

import diskcache

from dogpile.cache.api import CacheBackend, NO_VALUE
from dogpile.cache import register_backend

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FanoutCacheBackend(CacheBackend):
    def __init__(self, arguments):

        directory = arguments.get('directory')
        self.default_expire = arguments.get('default_expire')

        if directory is None:
            raise Exception()

        # TODO: move arguments to somewhere...
        self.cache = diskcache.FanoutCache(
            directory,
            timeout=10,
            statistics=True,
            shards=32,                 # default 8
            size_limit=2**30*5,       # 1073741824 * 5
            disk_min_file_size=2**20)  # 1048576

    def get(self, key):
        return self.cache.get(key, default=NO_VALUE)

    def set(self, key, value):
        self.cache.set(key, value, expire=self.default_expire)

    def delete(self, key):
        self.cache.pop(key)


register_backend('fanout', "toukka.adapted.dogpile_diskcache_backend", "FanoutCacheBackend")

# END
