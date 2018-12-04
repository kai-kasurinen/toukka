#

from werkzeug.contrib.cache import SimpleCache, FileSystemCache
from xdg.BaseDirectory import save_cache_path

#_cache_dir = save_cache_path('toukka', 'werkzeug', 'filesystemcache')
#cache = SimpleCache(threshold=1000, default_timeout=3600)
#cache = FileSystemCache(_cache_dir, threshold=1000, default_timeout=3600)


