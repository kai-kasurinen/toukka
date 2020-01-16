#

import os
import json
import logging
import time

from xdg.BaseDirectory import save_cache_path
from sqlitedict import SqliteDict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _get_uriban_database_file():
    return os.path.join(save_cache_path('toukka', 'spotify_manager'), 'uriban.db')


def _get_rule_file():
    return os.path.join(save_cache_path('toukka', 'spotify_manager'), 'uriban-rules.json')


class UriBanDict(SqliteDict):
    def __init__(self):
        super().__init__(
            filename=_get_uriban_database_file(),
            tablename='uriban',
            autocommit=True,
            encode=json.dumps,
            decode=json.loads)

    def add(self, uri, reason=None):
        key = uri
        value = {
            'reason': reason,
            'added_ts': time.time()
        }

        self[key] = value
        logger.debug('added: %s: %s', key, value)


class UriBan:
    def __init__(self):
        self.db = UriBanDict()


# END
