#

from beanbag.v2 import BeanBag, GET
import urllib.parse

class ListenBrainz:
    def __init__(self, session=None):
        self.api = BeanBag('https://api.listenbrainz.org/1/',
                                      session=session,
                                      use_attrdict=False)

    def get_listens(self, username):
        return GET(self.api.user()[username].listens())

    def get_latest_import(self, username):
        return GET(self.api['latest-import'](user_name=username))

    def get_user_url(self, username):
        BASE_URL = 'https://listenbrainz.org'
        return urllib.parse.urljoin(BASE_URL, username)
