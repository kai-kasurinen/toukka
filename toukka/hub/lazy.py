#

import os
import logging
import requests
import warnings

import cachecontrol
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from requests.packages.urllib3.util.retry import Retry

from xdg.BaseDirectory import save_cache_path


import discogs_client
import wikidata.client

import lazy_property
import memcache
import diskcache
import werkzeug.contrib.cache

import toukka.discogs.fetchers

from toukka.spotify import Spotify
from toukka.spotify.client_credentials_manager import ClientCredentialsManager
from toukka.experimental.deprecated.musicbrainz import MusicBrainz
from toukka.metabrainz.acousticbrainz import AcousticBrainz
from toukka.utils import Singleton
from toukka.spotify2musicbrainz import Spotify2MusicBrainz
from toukka.finna import Finna
from toukka.spotify_history.first import SpotifyHistory



logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)


class Hub(metaclass=Singleton):

    @lazy_property.LazyProperty
    def _cache_path(self):
        return save_cache_path('toukka')

    @lazy_property.LazyProperty
    def werkzeug_simplecache(self):
        logger.debug('init werkzeug simplecache')
        simplecache = werkzeug.contrib.cache.SimpleCache(threshold=1000, default_timeout=3600)
        return simplecache

    @lazy_property.LazyProperty
    def werkzeug_filesystemcache(self):
        logger.debug('init werkzeug filesystemcache')
        cache_dir = save_cache_path('toukka', 'werkzeug', 'filesystemcache')
        filesystemcache = werkzeug.contrib.cache.FileSystemCache(cache_dir, threshold=1000, default_timeout=3600)
        return filesystemcache

    @lazy_property.LazyProperty
    def diskcache_fanoutcache(self):
        logger.debug('init diskcache fanoutcache')
        cache_dir = save_cache_path('toukka', 'diskcache', 'fanoutcache')
        fanoutcache = diskcache.FanoutCache(cache_dir, timeout=10)
        return fanoutcache

    @lazy_property.LazyProperty
    def memcache(self):
        logger.debug('init memcache')
        mcache = memcache.Client(['127.0.0.1:11211'], debug=1)
        return mcache

    @lazy_property.LazyProperty
    def session(self):
        logger.debug('init session')
        cache_path_cachecontrol = save_cache_path('toukka', 'cachecontrol')
        cache = FileCache(cache_path_cachecontrol)
        retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503])
        adapter = cachecontrol.CacheControlAdapter(cache, cache_etags=False, max_retries=retries)
        #adapter = cachecontrol.CacheControlAdapter(cache, max_retries=retries)
        #adapter = cachecontrol.CacheControlAdapter(cache)
        session = requests.Session()
        session.headers.update({'User-Agent': 'toukka/0.0.0'})
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @lazy_property.LazyProperty
    def spotify(self):
        logger.debug('init spotify')
        # TODO: add tokens to sqlite
        cache_path_tokens = save_cache_path('toukka', 'spotify', 'tokens')
        client_credentials_manager = ClientCredentialsManager(cache_directory=cache_path_tokens)
        spotify = Spotify(requests_session=self.session,
                          client_credentials_manager=client_credentials_manager)
        spotify.trace = False
        spotify.max_get_retries = 1  # default is 10
        return spotify

    @lazy_property.LazyProperty
    def musicbrainz(self):
        logger.debug('init musicbrainz')
        # FIXME: testing use _session_plain instead of _session_cached
        mb = MusicBrainz(session=self.session)
        return mb

    @lazy_property.LazyProperty
    def mbngs(self):
        return self.musicbrainz.mbngs

    @lazy_property.LazyProperty
    def acousticbrainz(self):
        logger.debug('init acousticbrainz')
        acousticbrainz = AcousticBrainz(session=self.session)
        return acousticbrainz

    @lazy_property.LazyProperty
    def discogs(self):
        logger.debug('init discogs')
        discogs = discogs_client.Client('toukka/0.0.0')
        # FIXME: not caching, probably need custom caching strategy
        #discogs._fetcher = toukka.discogs.fetchers.RequestsFetcherSession(session=self.session)
        return discogs

    @lazy_property.LazyProperty
    def finna(self):
        logger.debug('init finna')
        finna = Finna(session=self.session)
        return finna

    @lazy_property.LazyProperty
    def wikidata(self):
        logger.debug('init wikidata')
        #cache_policy=wikidata.cache.MemoryCachePolicy(max_size=1024)
        cache_policy = wikidata.cache.ProxyCachePolicy(self.diskcache_fanoutcache, timeout=86400, property_timeout=604800)
        #cache_policy = wikidata.cache.ProxyCachePolicy(self.diskcache_fanoutcache, timeout=3600, property_timeout=86400)
        wikidata_client = wikidata.client.Client(cache_policy=cache_policy)
        #wikidata_client = wikidata.client.Client()
        return wikidata_client

    @lazy_property.LazyProperty
    def spotify2musicbrainz(self):
        logger.debug('init spotify2musicbrainz')
        sqlite_database_file = os.path.join(save_cache_path('toukka'), 'toukka.sqlite')
        sp2mb = Spotify2MusicBrainz(hub=self, dbfile=sqlite_database_file)
        return sp2mb

    @lazy_property.LazyProperty
    def spotify_history(self):
        logger.debug('init spotify_history')
        sh = SpotifyHistory()
        return sh

    @lazy_property.LazyProperty
    def itunes(self):
        itunes.base.SESSION = self.session
        return itunes


    # FIXME: remove
    sp = spotify
    mb = musicbrainz


class Toukka(metaclass=Singleton):

    @lazy_property.LazyProperty
    def hub(self):
        return Hub()

    @lazy_property.LazyProperty
    def sp(self):
        return self.hub.spotify

    @lazy_property.LazyProperty
    def mb(self):
        return self.hub.mb

    @lazy_property.LazyProperty
    def mbngs(self):
        return self.hub.mbngs

    @lazy_property.LazyProperty
    def acousticbrainz(self):
        return self.hub.acousticbrainz

    @lazy_property.LazyProperty
    def discogs(self):
        return self.hub.discogs

    @lazy_property.LazyProperty
    def sp2mb(self):
        return self.hub.spotify2musicbrainz

    @lazy_property.LazyProperty
    def finna(self):
        return self.hub.finna


# END
