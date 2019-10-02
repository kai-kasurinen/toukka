#

import logging

import sqlitedict
import json

import xdg.BaseDirectory
import os.path


class StateDB:
    def __init__(self, database_file, tablename):
        # cos "opening Sqlite table" is on INFO
        logging.getLogger('sqlitedict').setLevel(logging.WARNING)
        self._db = sqlitedict.SqliteDict(database_file,
                                         tablename=tablename,
                                         autocommit=False,
                                         encode=json.dumps,
                                         decode=json.loads)

    def get(self, key):
        return self._db.get(key)

    def set(self, key, value):
        self._db[key] = value
        self._db.commit()

#


def get_statedb():
    database_path = xdg.BaseDirectory.save_cache_path('toukka-sopiva', 'state')
    database_file = os.path.join(database_path, 'spotify.db')
    return StateDB(database_file, 'state')


# END
