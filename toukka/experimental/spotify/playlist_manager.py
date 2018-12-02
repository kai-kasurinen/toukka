#

from toukka import Toukka
from toukka.cache.diskcache import cache


class Playlists:
    @cache.memoize()
    def user_playlists_all(self, user):
        toukka = Toukka()
        paging = toukka.sp.user_playlists(user)
        playlists = toukka.sp.aggregate_paging_results(paging)
        return playlists

