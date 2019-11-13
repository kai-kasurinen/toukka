#

import pprint

from dataclasses import dataclass

from spotipy.model.base import Item
from spotipy.client.base import SpotifyBase


@dataclass
class Episode(Item):
    pass


class SpotifyEpisode(SpotifyBase):
    def episode(
            self,
            episode_id: str,
            market: str = None
    ) -> Episode:
        json = self._get('episodes/' + episode_id, market=market)
        #return Episode(**json)
        return json
