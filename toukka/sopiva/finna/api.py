#

'''finna api'''

from beanbag.v2 import BeanBag, GET
import urllib.parse

from .fields import RECORD_FIELDS_DEFAULT, RECORD_FIELDS_ALL

# https://api.finna.fi/swagger-ui/?url=%2Fapi%2Fv1%3Fswagger
# https://www.kiwi.fi/pages/viewpage.action?pageId=53839221
# https://www.kiwi.fi/display/Finna/Finnan+avoin+rajapinta


class Finna:
    def __init__(self, session=None):
        self.api = BeanBag('https://api.finna.fi/api/v1/',
                                      session=session,
                                      use_attrdict=False)

    def record(self, rid, fields=RECORD_FIELDS_ALL):
        params = {'field[]': fields}
        return GET(self.api.record(params, id=rid))

    def search(self, lookfor):
        return GET(self.api.search(lookfor=lookfor))

    # https://finna.fi/Record/viola.632917
    def url(self, rid):
        BASE_URL = 'https://finna.fi/Record/'
        return urllib.parse.urljoin(BASE_URL, rid)
