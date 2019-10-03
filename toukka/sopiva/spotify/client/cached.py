#

import spotipy
import toukka.cache.dogpile


class CachedSpotify(spotipy.Spotify):

    @toukka.cache.dogpile.region.cache_on_arguments()
    def track(self, track_id, market=None):
        return super().track(track_id, market=market)

    @toukka.cache.dogpile.region.cache_on_arguments()
    def artist(self, artist_id):
        return super().artist(artist_id)

    @toukka.cache.dogpile.region.cache_on_arguments()
    def album(self, album_id, market=None):
        return super().album(album_id, market=market)


# END
