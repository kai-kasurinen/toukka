#

import xdg.BaseDirectory
import diskcache
from tekore import Spotify



def get_diskcache():
    dir = xdg.BaseDirectory.save_cache_path('toukka', 'diskcache_spotify')

    cache = diskcache.FanoutCache(
        dir,
        timeout=10,
        statistics=True,
        size_limit=2**31,          # 2147483648
        disk_min_file_size=2**20)  # 1048576

    return cache


spotify_diskcache = get_diskcache()

# NOTE: not working...
# NOTE: TypeError: cannot pickle '_thread.RLock' object

class SpotifyDiskcacheCached(Spotify):
    pass

