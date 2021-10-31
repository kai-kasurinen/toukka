#

import cachecontrol
import diskcache

from cachecontrol.cache import BaseCache


class FanOutCacheAdapter(BaseCache):
    def __init__(self, *args, **kwargs):
        self._fanoutcache = diskcache.FanoutCache(*args, **kwargs)

    def get(self, key):
        return self._fanoutcache.get(key)

    def set(self, key, value, expires=None):
        # TODO: support expires
        return self._fanoutcache.set(key, value)

    def delete(self, key):
        return self._fanoutcache.delete(key)


# END
