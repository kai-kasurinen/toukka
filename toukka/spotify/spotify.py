#

import logging
import functools
import spotipy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Spotify(spotipy.Spotify):

    @functools.lru_cache(maxsize=1024)
    def track(self, track_id):
        return super().track(track_id)

    @functools.lru_cache(maxsize=1024)
    def artist(self, artist_id):
        return super().artist(artist_id)

    @functools.lru_cache(maxsize=1024)
    def album(self, album_id):
        return super().album(album_id)

    @functools.lru_cache(maxsize=1024)
    def audio_features_one(self, track):
        return self.audio_features(track)[0]

    def get_playlist_by_uri(self, uri):
        username = uri.split(':')[2]
        playlist_id = uri.split(':')[4]
        return self.user_playlist(username, playlist_id)

    def aggregate_paging_results(self, paging):
        results = paging.get('items')
        while paging.get('next'):
            logger.debug('getting results %s/%s', paging.get('offset'), paging.get('total'))
            paging = self.next(paging)
            results.extend(paging.get('items'))
        return results

    @functools.lru_cache(maxsize=1024)
    def user_playlists_all(self, user):
        paging = self.user_playlists(user)
        playlists = self.aggregate_paging_results(paging)
        return playlists


# END
