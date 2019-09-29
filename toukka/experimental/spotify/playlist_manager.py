#

import logging

from toukka.hub import Toukka
from memorised.decorators import memorise

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Playlists:
    def __init__(self, user_id=None):
        self.toukka = Toukka()
        if user_id is None:
            user_id=self.toukka.sp.me().get('id')
        self.user_id=user_id

    @memorise(ttl=86400, parent_keys=['user_id'])
    def _playlists(self):
        paging = self.toukka.sp.user_playlists(self.user_id)
        playlists = self.toukka.sp.aggregate_paging_results(paging)
        ret = list()
        for playlist in playlists:
            ret.append(playlist.get('id'))
        return ret

    def playlists(self):
        playlist_ids = self._playlists()
        ret = list()
        for playlist_id in playlist_ids:
            ret.append(self.playlist(playlist_id))
        return ret

    def playlist(self, playlist_id):
        fields = '(!tracks)'
        return self.toukka.sp.playlist(playlist_id, fields=fields)
