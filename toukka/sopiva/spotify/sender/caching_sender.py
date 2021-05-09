#

import os.path
import json

import tekore
import sqlitedict
import xdg.BaseDirectory

from tekore._sender import Sender

# NOTE: does not work. keys stored, but not data


def _get_sqlite_filename():
    database_path = xdg.BaseDirectory.save_cache_path('toukka', 'spotify')
    database_file = os.path.join(database_path, 'tekore_cache.db')
    return database_file


class SqliteCachingSender(tekore.CachingSender):

    def __init__(self, max_size: int = None, sender: Sender = None):
        super().__init__(max_size, sender)

        self._cache = sqlitedict.SqliteDict(_get_sqlite_filename(),
                                            tablename='cache',
                                            autocommit=True)

# END
