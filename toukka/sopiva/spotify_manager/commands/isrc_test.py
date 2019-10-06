#

import pprint

import spotipy.convert
import tqdm

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history
from toukka.sopiva.spotify_manager.database.track_to_isrc import TrackToISRC


def isrc_test():
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


#

COMMANDS = [
    isrc_test,
    ]

# END
