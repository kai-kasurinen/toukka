#

import logging
import pandas

import toukka.cache.diskcache

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# cache = toukka.cache.diskcache.get_cache().cache('album_audio_features')
cache = toukka.cache.diskcache.get_cache()
# three month
expires = 60*60*24*30*3


# TODO: move and remove

def is_album_instrumental(album_id, spotify=None):

    if spotify is None:
        raise Exception()

    album_audio_features = spotify.album_audio_features(album_id)
    return album_audio_features.is_instrumental()

# END
