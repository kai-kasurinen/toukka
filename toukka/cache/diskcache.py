#

#import atexit
import logging

import diskcache
import xdg.BaseDirectory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# NOTE: cache.memoize works only with functions, not methods

def get_cache():
    dir = xdg.BaseDirectory.save_cache_path('toukka', 'diskcache')
    cache = diskcache.FanoutCache(
        dir)
    return cache


def check_cache():
    get_cache().check(fix=True)


def _print_stats():
    print(get_cache().stats())


def _print_cache():
    for i in list(get_cache()):
        print(i)


# NOTE: ?
# atexit.register(_print_cache)
# atexit.register(_print_stats)


# END
