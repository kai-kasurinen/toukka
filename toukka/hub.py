#

import os
import logging
import requests
import warnings

from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from xdg.BaseDirectory import save_cache_path


import discogs_client
import wikidata.client

from toukka.spotify import Spotify
from toukka.spotify.client_credentials_manager import ClientCredentialsManager
from toukka.musicbrainz import MusicBrainz
from toukka.metabrainz.acousticbrainz import AcousticBrainz
from toukka.utils import Singleton
from toukka.spotify2musicbrainz import Spotify2MusicBrainz
from toukka.finna import Finna

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class Hub(metaclass=Singleton):

    def __init__(self):
        self._init_cache_path()
        self._init_session()
        self._init_spotify()
        #self._init_spotify_with_oauth()
        self._init_discogs()
        self._init_musicbrainz()
        self._init_spotify2musicbrainz()
        self._init_finna()
        self._init_wikidata()

    def _init_cache_path(self):
        cache_path = save_cache_path('toukka')

    def _init_session(self):
        cache_path_cachecontrol = save_cache_path('toukka', 'cachecontrol')
        cache = FileCache(cache_path_cachecontrol)
        self._session_plain = requests.Session()
        self._session_plain.headers.update({'User-Agent': 'toukka/0.0.0'})
        self._session_cached = CacheControl(self._session_plain, cache)
        self._session = self._session_cached

    def _init_spotify(self):
        # TODO: add tokens to sqlite
        cache_path_tokens = save_cache_path('toukka', 'spotify', 'tokens')
        client_credentials_manager = ClientCredentialsManager(cache_directory=cache_path_tokens)
        self.sp = Spotify(requests_session=self._session,
                          client_credentials_manager=client_credentials_manager)
        self.sp.trace = False
        self.sp.max_get_retries = 1  # default is 10

    def _init_musicbrainz(self):
        self.mb = MusicBrainz()
        self.mbngs = self.mb.mbngs
        self.acousticbrainz = AcousticBrainz(session=self._session)

    def _init_discogs(self):
        self.discogs = discogs_client.Client('toukka/0.0.0')

    def _init_finna(self):
        self.finna = Finna(session=self._session)

    def _init_wikidata(self):
        self.wikidata = wikidata.client.Client()

    def _init_spotify2musicbrainz(self):
        self._sqlite_database_file = os.path.join(save_cache_path('toukka'), 'toukka.sqlite')
        self.sp2mb = Spotify2MusicBrainz(hub=self, dbfile=self._sqlite_database_file)


class Toukka(metaclass=Singleton):
    def __init__(self):
        self.hub = Hub()
        self.sp = self.hub.sp
        self.mb = self.hub.mb
        self.mbngs = self.hub.mbngs
        self.acousticbrainz = self.hub.acousticbrainz
        self.discogs = self.hub.discogs
        self.sp2mb = self.hub.sp2mb
        self.finna = self.hub.finna



# END
