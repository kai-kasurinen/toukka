#

import logging

import httpx
import hishel

def get_client():

        logging.getLogger('httpx').setLevel(logging.WARNING)

        # default file is ~/.hishel.sqlite
        # TODO: change path
        storage = hishel.SQLiteStorage()

        transport_http = httpx.HTTPTransport(retries=3)
        transport_cache = hishel.CacheTransport(transport=transport_http, storage=storage)

        return httpx.Client(transport=transport_cache, http2=True, timeout=30.0)

# END
