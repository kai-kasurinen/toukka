#

import pprint

from dataclasses import dataclass

from spotipy.model.base import Item
from spotipy.client.base import SpotifyBase

# https://github.com/librespot-org/librespot/commit/4a04e48f8a712f22feacfe61276b65d05bf775c8

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
