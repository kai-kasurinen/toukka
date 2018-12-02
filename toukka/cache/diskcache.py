#

import atexit

from diskcache import FanoutCache
from xdg.BaseDirectory import save_cache_path


cache = FanoutCache(save_cache_path('toukka', 'diskcache', 'fanoutcache'), timeout=10)
#cache.check(fix=True)


def _print_stats():
    print(cache.stats())

def _print_cache():
    for i in list(cache):
        print(i)

#atexit.register(_print_cache)
#atexit.register(_print_stats)


# END
