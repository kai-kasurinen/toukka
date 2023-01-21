#

import logging
import pandas

from .function_cache import cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# month
expires = 60*60*24*30


@cache.memoize(expire=expires, typed=True, ignore={'spotify'})
def is_album_instrumental(album_id, spotify=None):
    if spotify is None:
        raise Exception

    album = spotify.album(album_id)
    track_ids = [track.id for track in album.tracks.items]

    tracks_audio_features = spotify.tracks_audio_features(track_ids)
    # drop Nones
    tracks_audio_features = [item for item in tracks_audio_features if item is not None]

    if not tracks_audio_features:
        logger.warning('no audio features')
        return None

    tracks_audio_features_df = pandas.DataFrame(tracks_audio_features)

    instrumentalness_mean = tracks_audio_features_df['instrumentalness'].mean()

    logger.debug(instrumentalness_mean)

    if instrumentalness_mean > 0.5:
        return True
    else:
        return False

# END
