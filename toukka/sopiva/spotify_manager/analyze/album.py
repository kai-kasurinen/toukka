#

import logging
import functools
import operator
import collections
import pandas

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.model import FullPlaylistTrack

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def analyze_album(album_uri):
    spotify = get_spotify()

    album_id = spotify.convert.from_uri(album_uri).id

    album = spotify.album(album_id)
    printer(album)
    print()

    album = spotify.album(album_id)
    album_tracks = list(spotify.all_items(album.tracks))
    track_ids = [track.id for track in album_tracks]
    tracks = list(spotify.tracks(track_ids))
    album_audio_features = spotify.tracks_audio_features(track_ids)
    album_audio_features = [item for item in album_audio_features if item is not None]
    album_audio_features_df = pandas.DataFrame(album_audio_features)
    album_tracks_df = pandas.DataFrame(tracks)

    # TODO: simpletrack does not include popularity
    print(album_tracks_df['popularity'].describe())
    print()
    print(album_audio_features_df.describe())

# END
