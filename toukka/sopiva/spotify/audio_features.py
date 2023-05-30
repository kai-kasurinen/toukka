#

import logging
import pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TracksFeaturesDF:
    
    def __init__(self, tracks, tracks_audio_features):
        tracks_df = pandas.DataFrame(tracks)        
        audio_features_df = pandas.DataFrame(filter(None, tracks_audio_features))
        audio_features_df.drop(columns=['duration_ms', 'uri', 'type'], inplace=True)

        if len(tracks_df) != len(audio_features_df):
            logger.warning('some audio features missing: tracks %i, features %i',
                           len(tracks_df), len(audio_features_df))

        self.df = pandas.merge(tracks_df, audio_features_df, how='left', on=['id'])

    @property
    def instrumentalness(self):
        return self.df['instrumentalness']

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
