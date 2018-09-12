#

import logging
import requests

from beanbag.v2 import BeanBag, GET, BeanBagException
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from ..exceptions import MusicBrainzRateLimitException
from ..ratelimiter import musicbrainz_server_ratelimit_sleeper


logger = logging.getLogger(__name__)


class MusicBrainzWS2:
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
            retries = Retry(total=10, backoff_factor=2, status_forcelist=[500, 502, 503])
            session.mount('https://musicbrainz.org/ws/2/', HTTPAdapter(max_retries=retries))

        self.api = BeanBag('https://musicbrainz.org/ws/2/', session=session, use_attrdict=False)
        self.fmt = 'json'

    def _GET(self, url, body=None):
        musicbrainz_server_ratelimit_sleeper()
        try:
            return GET(url)
        except BeanBagException as error:
            if error.response.status_code == 503:
                logger.debug('hit musicbrainz ratelimiting')
                raise MusicBrainzRateLimitException(error.response, 'musicbrainz ratelimiting')
            else:
                raise

    def _GET_ENTITY(self, entity_type, mbid, includes=None):
        return self._GET(self.api[entity_type][mbid](fmt=self.fmt, inc=includes))

    def _BROWSE_ENTITY(self, entity_type, filters, limit=None, offset=None, includes=None):
        return self._GET(self.api[entity_type](filters, fmt=self.fmt, limit=limit, offset=offset, inc=includes))

    def area(self, mbid, includes=None):
        return self._GET_ENTITY('area', mbid, includes=includes)

    def artist(self, mbid, includes=None):
        return self._GET_ENTITY('artist', mbid, includes=includes)

    def event(self, mbid, includes=None):
        return self._GET_ENTITY('event', mbid, includes=includes)

    def instrument(self, mbid, includes=None):
        return self._GET_ENTITY('instument', mbid, includes=includes)

    def label(self, mbid, includes=None):
        return self._GET_ENTITY('label', mbid, includes=includes)

    def place(self, mbid, includes=None):
        return self._GET_ENTITY('place', mbid, includes=includes)

    def recording(self, mbid, includes=None):
        return self._GET_ENTITY('recording', mbid, includes=includes)

    def release(self, mbid, includes=None):
        return self._GET_ENTITY('release', mbid, includes=includes)

    def release_group(self, mbid, includes=None):
        return self._GET_ENTITY('release-group', mbid, includes=includes)

    def series(self, mbid, includes=None):
        return self._GET_ENTITY('series', mbid, includes=includes)

    def work(self, mbid, includes=None):
        return self._GET_ENTITY('work', mbid, includes=includes)

    def url(self, mbid, includes=None):
        return self._GET_ENTITY('url', mbid, includes=includes)

    def discid(self, discid, includes=None, toc=None):
        return self._GET_ENTITY('discid', discid, includes=includes, toc=toc)

    def isrc(self, isrc, includes=None):
        return self._GET_ENTITY('isrc', isrc, includes=includes)

    def iswc(self, iswc, includes=None):
        return self._GET_ENTITY('iswc', iswc, includes=includes)


# END
