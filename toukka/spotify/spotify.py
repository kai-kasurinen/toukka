#

import logging
import functools
import spotipy


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

    def audio_features_one(self, track):
        return self.audio_features(track)[0]

    def get_playlist_by_uri(self, uri):
        username = uri.split(':')[2]
        playlist_id = uri.split(':')[4]
        return self.user_playlist(username, playlist_id)





#
