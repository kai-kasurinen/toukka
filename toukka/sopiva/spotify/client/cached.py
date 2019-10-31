#

from typing import Union
import logging
import spotipy.client
from spotipy.model import FullTrack, FullArtist, FullAlbum, AudioFeatures, AudioAnalysis

import toukka.cache.dogpile


logger = logging.getLogger(__name__)


# TODO: rename cached methods
# TODO: do something when pickling fails?
# TODO: handle from_token
# TODO: or not use at all?


class SpotifyCached(spotipy.client.Spotify):

    @toukka.cache.dogpile.redis.cache_on_arguments()
    def track(self,
              track_id: str,
              market: Union[str, None] = 'from_token'
              ) -> FullTrack:
        if market == 'from_token':
            logger.warning('market from_token and caching')
        return super().track(track_id, market=market)

    @toukka.cache.dogpile.redis.cache_on_arguments()
    def artist(self,
               artist_id: str
               ) -> FullArtist:
        return super().artist(artist_id)

    @toukka.cache.dogpile.redis.cache_on_arguments()
    def album(self,
              album_id: str,
              market: Union[str, None] = 'from_token'
              ) -> FullAlbum:
        if market == 'from_token':
            logger.warning('market from_token and caching')
        return super().album(album_id, market=market)

    # NOTE: not cached by cachecontrol at all
    @toukka.cache.dogpile.redis.cache_on_arguments()
    def track_audio_features(self, track_id: str) -> AudioFeatures:
        return super().track_audio_features(track_id)

    @toukka.cache.dogpile.redis.cache_on_arguments()
    def track_audio_analysis(self, track_id: str) -> AudioAnalysis:
        return super().track_audio_analysis(track_id)

# END
