#

from beanbag.v2 import BeanBag, GET
import urllib.parse

class AcousticBrainz:
    def __init__(self, session=None):
        self.acousticbrainz = BeanBag('https://acousticbrainz.org/api/v1/',
                                      session=session,
                                      use_attrdict=False)

    def get_count(self, mbid):
        return GET(self.acousticbrainz[mbid]['count'])

    def get_low_level(self, mbid, number=0):
        return GET(self.acousticbrainz[mbid]['low-level'](n=number))

    def get_high_level(self, mbid, number=0):
        return GET(self.acousticbrainz[mbid]['high-level'](n=number))

    def get_url(self, mbid):
        BASE_URL = 'https://acousticbrainz.org/'
        return urllib.parse.urljoin(BASE_URL, mbid)
