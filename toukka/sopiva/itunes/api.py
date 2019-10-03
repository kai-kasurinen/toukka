#

from beanbag.v2 import BeanBag, GET
import urllib.parse

class iTunesBeanBag(BeanBag):
    mime_json = 'text/javascript'

class iTunesAPI:
    def __init__(self, session=None):
        self.itunes = iTunesBeanBag('https://itunes.apple.com/',
                                      session=session,
                                      use_attrdict=False)

    def search(self, **kwargs):
        return GET(self.itunes.search(**kwargs))

    def lookup(self, **kwargs):
        return GET(self.itunes.lookup(**kwargs))

