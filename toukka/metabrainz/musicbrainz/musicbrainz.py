#

from .search import MusicBrainzSearch
from .ws2 import MusicBrainzWS2


class MusicBrainz:
    def __init__(self, session=None):
        self._search = MusicBrainzSearch(session=session)
        self._ws2 = MusicBrainzWS2(session=session)


# END
