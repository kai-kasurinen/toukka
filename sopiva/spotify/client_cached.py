#

from spotipy import Spotify
from sopiva.cache.dogpile import region


class CachedSpotify(Spotify):

    @region.cache_on_arguments()
    def track(self, track_id, market):
        return super().track(track_id, market=market)

    @region.cache_on_arguments()
    def artist(self, artist_id):
        return super().artist(artist_id)

    @region.cache_on_arguments()
    def album(self, album_id, market):
        return super().album(album_id, market=market)


# END
