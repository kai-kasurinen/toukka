#

'''Track to ISRC database'''

import logging
import json
import os.path

import sqlitedict
import xdg.BaseDirectory


class TrackToISRC:
    '''Track to ISRC database'''
    def __init__(self):
        database_path = xdg.BaseDirectory.save_cache_path('toukka', 'spotify')
        database_file = os.path.join(database_path, 'track_to_isrc.db')
        tablename = 'track_isrc'
        # cos "opening Sqlite table" is on INFO
        logging.getLogger('sqlitedict').setLevel(logging.WARNING)
        self._db = sqlitedict.SqliteDict(database_file,
                                         tablename=tablename,
                                         autocommit=False,
                                         encode=json.dumps,
                                         decode=json.loads)

    def get(self, key):
        '''get ISRC'''
        return self._db.get(key)

    def set(self, key, value):
        '''set ISRC'''
        self._db[key] = value
        self._db.commit()


# END
