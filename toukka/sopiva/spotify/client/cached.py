#

from typing import Union
import logging
import functools

import spotipy.client
from spotipy.model import FullTrack, FullArtist, FullAlbum, AudioFeatures, AudioAnalysis

import toukka.cache.dogpile

logger = logging.getLogger(__name__)

# TODO: do something when pickling fails?


def check_from_token(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if kwargs.get('market') != 'from_token':
            return f(*args, **kwargs)
        else:
            raise Exception('market is from_token')
    return wrapper


class SpotifyCached(spotipy.client.Spotify):

    track = toukka.cache.dogpile.redis.cache_on_arguments()(spotipy.client.Spotify.track)
    track = check_from_token(track)

    artist = toukka.cache.dogpile.redis.cache_on_arguments()(spotipy.client.Spotify.artist)

    album = toukka.cache.dogpile.redis.cache_on_arguments()(spotipy.client.Spotify.album)
    album = check_from_token(track)

    track_audio_features = toukka.cache.dogpile.redis.cache_on_arguments()(spotipy.client.Spotify.track_audio_features)
    track_audio_analysis = toukka.cache.dogpile.redis.cache_on_arguments()(spotipy.client.Spotify.track_audio_analysis)


# END
