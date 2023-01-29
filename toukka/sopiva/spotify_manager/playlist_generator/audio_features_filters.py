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


def is_album_instrumental(album_id, spotify=None):

    @cache.memoize(expire=expires, typed=True)
    def get_album_audio_features(album_id):
        album = spotify.album(album_id)
        album_tracks = spotify.all_items(album.tracks)
        track_ids = [track.id for track in album_tracks]
        album_audio_features = spotify.tracks_audio_features(track_ids)
        album_audio_features = [item for item in album_audio_features if item is not None]
        if len(track_ids) != len(album_audio_features):
            logger.warning('album_audio_features len mismatch: tracks %i, features: %i',
                           len(track_ids), len(album_audio_features))
        return album_audio_features
        # END

    if spotify is None:
        raise Exception()

    album_audio_features = get_album_audio_features(album_id)

    if not album_audio_features:
        logger.warning('no album audio features')
        return False

    album_audio_features_df = pandas.DataFrame(album_audio_features)

    album_instrumentalness_mean = album_audio_features_df['instrumentalness'].mean()
    album_instrumentalness_min = album_audio_features_df['instrumentalness'].min()
    album_instrumentalness_max = album_audio_features_df['instrumentalness'].max()

    logger.debug('min: %.4f, mean: %.4f, max: %.4f',
                 album_instrumentalness_min, album_instrumentalness_mean, album_instrumentalness_max)

    # NOTE: album_instrumentalness_min filters too much, use album_instrumentalness_mean
    if album_instrumentalness_min > 0.5:
        return True
    else:
        return False

# END
