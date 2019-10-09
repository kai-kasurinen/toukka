#

import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify


def track_info(uri: str,
               market: str = None):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    track = spotify.track(uri_id, market=market)
    track.pprint()


COMMANDS = [
    track_info
    ]
