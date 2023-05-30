#

import logging
import functools
import operator
import collections
import pandas

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.model import FullPlaylistTrack
from toukka.sopiva.spotify.audio_features import TracksFeaturesDF

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: first test and then split
# TODO: use pandas (dataclasses support needs 1.1)

# TODO: CLEAN UP TESTINGS

def analyze_playlist(playlist_uri=None):
    spotify = get_spotify()

    playlist_uri = playlist_uri or spotify.currently_playing_playlist()

    if playlist_uri is None:
        raise Exception()

    playlist_id = spotify.convert.from_uri(playlist_uri).id

    playlist = spotify.playlist(playlist_id)
    printer(playlist)
    print()

    playlist_items = spotify.all_items(spotify.playlist_items(playlist.id))
    playlist_items_counter = collections.Counter()
    tracks_ids = list()
    tracks = list()

    for playlist_item in playlist_items:
        # TODO: print count track types
        # TODO: print added_at timerange and added_by counts
        if playlist_item.track is None:
            continue
        if not isinstance(playlist_item.track, FullPlaylistTrack):
            continue
        tracks_ids.append(playlist_item.track.id)
        tracks.append(playlist_item.track)

    tracks_features = spotify.tracks_features_df(tracks_ids)
    print(tracks_features.df.describe())



# END
