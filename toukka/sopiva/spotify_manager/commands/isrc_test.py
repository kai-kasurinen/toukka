#

import pprint

import spotipy.convert
import tqdm

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history


def isrc_test():
    '''update isrc database or something'''

    spotify = get_spotify()
    spotify_history = get_spotify_history()

    history_unique_tracks_ids = spotify_history.get_all_unique_track_ids()
    print(f'history has {len(history_unique_tracks_ids)} unique track ids')

    isrcs = set()
    for counter, track_uri in enumerate(history_unique_tracks_ids, start=1):

        if 'spotify:track:' not in track_uri:
            print(f'unsupported track_uri: {track_uri}')
            continue

        uri_type, uri_id = spotipy.convert.from_uri(track_uri)
        track = spotify.track(uri_id)
        isrc = track.external_ids.get('isrc')
        print(f'{counter} {track_uri} {isrc}')
        isrcs.add(isrc)


#

COMMANDS = [
    isrc_test,
    ]

# END
