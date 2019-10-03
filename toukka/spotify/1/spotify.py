#

import logging
import functools
import spotipy

from memorised.decorators import memorise

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Spotify(spotipy.Spotify):

    #def __init__(self, *args, **kwargs):
    #    self.cache = kwargs.pop('cache', None)
    #    super().__init__(*args, **kwargs)

    @memorise(ttl=86400)
    def track(self, track_id):
        return super().track(track_id)

    @memorise(ttl=86400)
    def artist(self, artist_id):
        return super().artist(artist_id)

    @memorise(ttl=86400)
    def album(self, album_id):
        return super().album(album_id)

    # https://github.com/plamere/spotipy/pull/320
    @memorise(ttl=86400)
    def playlist(self, playlist_id, fields=None, market=None):
            plid = self._get_id('playlist', playlist_id)
            return self._get("playlists/%s" % (plid), fields=fields)

    @memorise(ttl=86400)
    def user_playlist(self, user, playlist_id=None, fields=None):
        return super().user_playlist(user, playlist_id, fields)

    @memorise(ttl=86400)
    def audio_features_one(self, track_id):
        return self.audio_features(track_id)[0]

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

    # FIXME: memorise does not work with this when user has many playlists
    #@memorise(ttl=86400)
    def user_playlists_all(self, user):
        paging = self.user_playlists(user)
        playlists = self.aggregate_paging_results(paging)
        return playlists


# END
