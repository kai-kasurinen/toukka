#

from itertools import chain

import tekore.client.api.search
import tekore.convert

from tekore.serialise import SerialisableEnum
from tekore.client.base import SpotifyBase
from tekore.client.decor import send_and_process
from tekore.client.process import single, model_list

from ..model.podcast import Episode, Show, EpisodePaging, ShowPaging


class SpotifyPodcast(SpotifyBase):

    @send_and_process(single(Episode))
    def episode(
            self,
            episode_id: str,
            market: str
    ) -> Episode:
        return self._get('episodes/' + episode_id, market=market)

    @send_and_process(single(Show))
    def show(
            self,
            show_id: str,
            market: str
    ) -> Show:
        return self._get('shows/' + show_id, market=market)


_paging_type = {
    'episode': EpisodePaging,
    'show': ShowPaging
}

tekore.client.api.search.paging_type.update(_paging_type)


class _IdentifierType(SerialisableEnum):
    show = 'show'
    episode = 'episode'


IdentifierTypePatched = SerialisableEnum('IdentifierType',
                                         [(i.name, i.value) for i in chain(
                                             tekore.convert.IdentifierType,
                                             _IdentifierType)])

tekore.convert.IdentifierType = IdentifierTypePatched

# END
