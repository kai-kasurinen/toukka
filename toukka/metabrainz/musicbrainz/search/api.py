#

import logging
import requests

from beanbag.v2 import BeanBag, GET, BeanBagException
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from ..exceptions import MusicBrainzRateLimitException
from ..ratelimiter import musicbrainz_server_ratelimit_sleeper


logger = logging.getLogger(__name__)


class MusicBrainzSearch:
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
            retries = Retry(total=10, backoff_factor=2, status_forcelist=[500, 502, 503])
            session.mount('https://search.musicbrainz.org/ws/2/', HTTPAdapter(max_retries=retries))

        self.api = BeanBag('https://search.musicbrainz.org/ws/2/', session=session, use_attrdict=False)
        self.fmt = 'jsonnew'

    def _GET(self, url, body=None):
        musicbrainz_server_ratelimit_sleeper()
        try:
            return GET(url)
        except BeanBagException as error:
            if error.response.status_code == 503:
                logger.debug('hit musicbrainz ratelimiting')
                raise MusicBrainzRateLimitException(error.response, 'MusicBrainz server ratelimiting')
            else:
                raise

    def artist(self, query, limit=25, offset=None):
        return self._GET(self.api.artist(type='artist', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def track(self, query, limit=25, offset=None):
        return self._GET(self.api.track(type='track', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def recording(self, query, limit=25, offset=None):
        return self._GET(self.api.recording(type='recording', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def release(self, query, limit=25, offset=None):
        return self._GET(self.api.release(type='release', fmt=self.fmt, limit=limit, offset=offset, query=query))


# END
