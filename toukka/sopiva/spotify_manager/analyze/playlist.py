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


# TODO: first test and then split
# TODO: use pandas (dataclasses support needs 1.1)


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

    tracks_dataframe = pandas.DataFrame(tracks)
    print(tracks_dataframe['popularity'].describe())
    print()

    tracks_features = spotify.tracks_audio_features(tracks_ids)

    # NOTE: we drop Nones
    tracks_features = (item for item in tracks_features if item is not None)
    # tracks_features = filter(functools.partial(operator.is_not, None), tracks_features)

    # NOTE: DataFrame fails when features has Nones
    tracks_features_dataframe = pandas.DataFrame(tracks_features)
    #tracks_features_dataframe['duration_ms'] = pandas.to_timedelta(
    #    tracks_features_dataframe['duration_ms'], unit='ms')
    #print(tracks_features_dataframe.dtypes)
    print(tracks_features_dataframe.describe())


# END
