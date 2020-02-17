#

from tekore.client.base import SpotifyBase
from ..model.podcast import Episode, Show


class SpotifyPodcast(SpotifyBase):

    def episode(
            self,
            episode_id: str,
            market: str
    ) -> Episode:
        json = self._get('episodes/' + episode_id, market=market)
        return Episode(**json)

    def show(
            self,
            show_id: str,
            market: str
    ) -> Show:
        json = self._get('shows/' + show_id, market=market)
        return Show(**json)


# END
