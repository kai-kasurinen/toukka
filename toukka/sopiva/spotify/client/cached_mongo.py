#

from tekore.client import Spotify
from tekore.model import FullTrack
from toukka.cache.dogpile import mongo

# TODO: it works, but needs...


class SpotifyMongo(Spotify):

    def track(self, track_id: str, market: str = None) -> FullTrack:
        json = self.track_json(track_id, market=market)
        return FullTrack(**json)

    @mongo.cache_on_arguments()
    def track_json(self, track_id: str, market: str = None):
        json = self._get('tracks/' + track_id, market=market)
        return json


# END
