#

import logging
import pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# disc_number   duration_ms  track_number  popularity
#
# acousticness  danceability energy  instrumentalness
# key    liveness    loudness  mode  speechiness
# tempo  time_signature     valence


AUDIO_FEATURES_COLUMNS = [
    'id', 'acousticness', 'analysis_url',
    'danceability', 'duration_ms', 'energy', 'instrumentalness',
    'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo',
    'time_signature', 'track_href', 'type', 'uri', 'valence']


class TracksFeaturesDF:

    def __init__(self, tracks, tracks_audio_features):

        tracks_dict = [model.__dict__ for model in tracks]
        tracks_audio_features_dict = [model.__dict__ for model in tracks_audio_features if model is not None]

        tracks_df = pandas.DataFrame(tracks_dict)
        audio_features_df = pandas.DataFrame(tracks_audio_features_dict)

        if audio_features_df.empty:
            logger.warning('No audio features available')
            audio_features_df = pandas.DataFrame(columns=AUDIO_FEATURES_COLUMNS)

        audio_features_df.drop(columns=['duration_ms', 'uri', 'type'], inplace=True)

        if len(tracks_df) != len(audio_features_df):
            logger.warning('some audio features missing: tracks %i, features %i',
                           len(tracks_df), len(audio_features_df))

        self.df = pandas.merge(tracks_df, audio_features_df, how='left', on=['id'])

    @property
    def popularity(self):
        return self.df['popularity']

    @property
    def acousticness(self):
        return self.df['acousticness']

    @property
    def danceability(self):
        return self.df['danceability']

    @property
    def energy(self):
        return self.df['energy']

    @property
    def instrumentalness(self):
        return self.df['instrumentalness']

    @property
    def key(self):
        return self.df['key']

    @property
    def liveness(self):
        return self.df['liveness']

    @property
    def loudness(self):
        return self.df['loudness']

    @property
    def mode(self):
        return self.df['mode']

    @property
    def speechiness(self):
        return self.df['speechiness']

    @property
    def tempo(self):
        return self.df['tempo']

    @property
    def time_signature(self):
        return self.df['time_signature']

    @property
    def valence(self):
        return self.df['valence']

    # END


class AlbumFeaturesDF(TracksFeaturesDF):

    def is_instrumental(self):

        instrumentalness_mean = self.instrumentalness.mean()
        instrumentalness_min = self.instrumentalness.min()
        instrumentalness_max = self.instrumentalness.max()

        logger.debug('min: %.4f, mean: %.4f, max: %.4f',
                     instrumentalness_min, instrumentalness_mean, instrumentalness_max)

        # NOTE: instrumentalness_min filters too much, use instrumentalness_mean
        if instrumentalness_min > 0.5:
            return True
        else:
            return False

    # END


# END
