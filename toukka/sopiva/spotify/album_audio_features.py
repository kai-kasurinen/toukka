#

import logging
import pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AlbumAudioFeatures:
    
    def __init__(self, album_tracks, album_audio_features):
        self.tracks = album_tracks
        
        # NOTE: remove Nones
        album_audio_features = [item for item in album_audio_features if item is not None]
        self.album_audio_features = album_audio_features

        if len(self.tracks) != len(self.album_audio_features):
            logger.warning('album_audio_features len mismatch: tracks %i, features: %i',
                           len(self.tracks), len(self.album_audio_features))

        self.dataframe = pandas.DataFrame(self.album_audio_features)

    @property
    def instrumentalness(self):
        return self.dataframe['instrumentalness']


    def is_instrumental(self):

        album_instrumentalness_mean = self.instrumentalness.mean()
        album_instrumentalness_min = self.instrumentalness.min()
        album_instrumentalness_max = self.instrumentalness.max()

        logger.debug('min: %.4f, mean: %.4f, max: %.4f',
                    album_instrumentalness_min, album_instrumentalness_mean, album_instrumentalness_max)

        # NOTE: album_instrumentalness_min filters too much, use album_instrumentalness_mean
        if album_instrumentalness_min > 0.5:
            return True
        else:
            return False

    # END


# END
