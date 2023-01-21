#

import logging

import diskcache
import xdg.BaseDirectory


def get_cache():
    dir = xdg.BaseDirectory.save_cache_path('toukka', 'spotify_manager', 'playlist_generator_function_cache')
    cache = diskcache.FanoutCache(
        dir)
    return cache


cache = get_cache()

# END
