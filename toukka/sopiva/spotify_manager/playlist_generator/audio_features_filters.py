#

import logging
import pandas

import toukka.cache.diskcache

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def is_album_instrumental(album_id, spotify=None):

    if spotify is None:
        raise Exception()

    cache = toukka.cache.diskcache.get_cache().cache('album_audio_features')
    # three month
    expires = 60*60*24*30*3

    @cache.memoize(expire=expires, typed=True)
    def get_album_audio_features(album_id):
        album = spotify.album(album_id)
        album_tracks = spotify.all_items(album.tracks)
        track_ids = [track.id for track in album_tracks]
        album_audio_features = spotify.tracks_audio_features(track_ids)
        album_audio_features = [item for item in album_audio_features if item is not None]
        if len(track_ids) == len(album_audio_features):
            logger.warning('album_audio_features len mismatch: tracks %i, features: %i',
                           len(track_ids), len(album_audio_features))
        return album_audio_features

    def get_album_audio_features_df(album_id):
        album_audio_features = get_album_audio_features(album_id)
        if not album_audio_features:
            logger.debug('no album audio features')
            return None
        album_audio_features_df = pandas.DataFrame(album_audio_features)
        return album_audio_features_df

    album_audio_features_df = get_album_audio_features_df(album_id)

    if album_audio_features_df is None:
        logger.debug('no album audio features df')
        return False

    album_instrumentalness_mean = album_audio_features_df['instrumentalness'].mean()
    album_instrumentalness_min = album_audio_features_df['instrumentalness'].min()
    album_instrumentalness_max = album_audio_features_df['instrumentalness'].max()

    if album_instrumentalness_mean is None:
        logger.debug('no album instrumentalness mean')
        return False

    if album_instrumentalness_min is None:
        logger.debug('no album instrumentalness mean')
        return False

    logger.debug('min: %.4f, mean: %.4f, max: %.4f',
                 album_instrumentalness_min, album_instrumentalness_mean, album_instrumentalness_max)

    if album_instrumentalness_min > 0.5:
        return True
    else:
        return False

# END
