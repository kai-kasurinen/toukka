#

from typing import Union

from spotipy.model import FullTrack, FullArtist, FullAlbum, AudioFeatures

import toukka.cache.dogpile
from .extented import SpotifyExtended


class SpotifyCached(SpotifyExtended):

    @toukka.cache.dogpile.region.cache_on_arguments()
    def track(self,
              track_id: str,
              market: Union[str, None] = 'from_token'
              ) -> FullTrack:
        return super().track(track_id, market=market)

    @toukka.cache.dogpile.region.cache_on_arguments()
    def artist(self,
               artist_id: str
               ) -> FullArtist:
        return super().artist(artist_id)

    @toukka.cache.dogpile.region.cache_on_arguments()
    def album(self,
              album_id: str,
              market: Union[str, None] = 'from_token'
              ) -> FullAlbum:
        return super().album(album_id, market=market)

    @toukka.cache.dogpile.region.cache_on_arguments()
    def track_audio_features(self, track_id: str) -> AudioFeatures:
        return super().track_audio_features(track_id)

# END
