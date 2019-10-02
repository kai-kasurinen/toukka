#

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from .search import MusicBrainzSearch
from .ws2 import MusicBrainzWS2


class MusicBrainz:
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
            retries = Retry(total=10, backoff_factor=2, status_forcelist=[500, 502, 503])
            session.mount('https://musicbrainz.org/ws/2/', HTTPAdapter(max_retries=retries))
            session.mount('https://search.musicbrainz.org/ws/2/', HTTPAdapter(max_retries=retries))

        self._search = MusicBrainzSearch(session=session)
        self._ws2 = MusicBrainzWS2(session=session)


# END
