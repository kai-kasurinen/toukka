#

from diskcache import FanoutCache
from xdg.BaseDirectory import save_cache_path


cache = FanoutCache(save_cache_path('toukka', 'diskcache', 'fanoutcache'), timeout=10)

# END
