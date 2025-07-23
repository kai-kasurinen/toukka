#

import logging
import os

import sqlite3
import httpx
import hishel

from xdg.BaseDirectory import save_cache_path

from toukka.cache.durations import WEEK

def get_client_():
        return httpx.Client(http2=True)

def get_client():

        logging.getLogger('httpx').setLevel(logging.WARNING)

        cache_file = os.path.join(save_cache_path('toukka'), 'hishel.sqlite')

        storage = hishel.SQLiteStorage(connection=sqlite3.connect(cache_file), ttl=WEEK)

        transport_http = httpx.HTTPTransport(retries=3)
        transport_cache = hishel.CacheTransport(transport=transport_http, storage=storage)

        return httpx.Client(transport=transport_cache, http2=True, timeout=30.0)

# END
