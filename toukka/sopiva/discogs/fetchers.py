#

import requests

from discogs_client.fetchers import Fetcher



class RequestsFetcherSession(Fetcher):
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
        self.session = session

    def fetch(self, client, method, url, data=None, headers=None, json=True):
        resp = self.session.request(method, url, data=data, headers=headers)
        return resp.content, resp.status_code
