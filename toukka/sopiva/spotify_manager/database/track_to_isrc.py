#

'''Track to ISRC database'''

import logging
import json
import os.path

import sqlitedict
import xdg.BaseDirectory
import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history



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


#

def track_to_isrc_update():
    '''update isrc database or something'''

    spotify = get_spotify()
    spotify_history = get_spotify_history()
    track_to_isrc = TrackToISRC()

    history_unique_tracks_ids = spotify_history.get_all_unique_track_ids()
    print(f'history has {len(history_unique_tracks_ids)} unique track ids')

    for counter, track_uri in enumerate(history_unique_tracks_ids, start=1):

        # 'cos convert.from_uri does not handle podcasts and other
        if 'spotify:track:' not in track_uri:
            print(f'{counter} {track_uri}: unsupported type')
            continue

        track_uri_type, track_uri_id = spotipy.convert.from_uri(track_uri)

        # check before we get track from spotify api
        if track_to_isrc.get(track_uri_id):
            print(f'{counter} {track_uri}: already on database')
            continue

        track = spotify.track(track_uri_id)
        isrc = track.external_ids.get('isrc')
        track_to_isrc.set(track.id, isrc)
        print(f'{counter} {track_uri} {isrc}')


# FIXME: hack and slow
def get_listened_isrcs():
    '''get listened isrcs'''

    spotify_history = get_spotify_history()
    track_to_isrc = TrackToISRC()
    history_unique_tracks_ids = spotify_history.get_all_unique_track_ids()
    print(f'history has {len(history_unique_tracks_ids)} unique track ids')

    isrcs = set()
    for counter, track_uri in enumerate(history_unique_tracks_ids, start=1):
        # 'cos convert.from_uri does not handle podcasts and other
        if 'spotify:track:' not in track_uri:
            # print(f'{counter} {track_uri}: unsupported type')
            continue
        track_uri_type, track_uri_id = spotipy.convert.from_uri(track_uri)
        isrc = track_to_isrc.get(track_uri_id)
        if isrc is None:
            continue
        isrcs.add(isrc)
    print(f'history has {len(isrcs)} unique ISRCs')
    return isrcs



# END
