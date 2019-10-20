#
#

import logging
import pprint
import itertools
import types
import collections
import random

import spotipy.convert
import spotipy.serialise
import spotipy.model.track
import spotipy.model.artist
import spotipy.model.playlist
import spotipy.model.album

import toukka.config

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history
from toukka.sopiva.spotify.printer import first as printer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _get_playlist_uri_from_config():
    return toukka.config.lazy_config['spotify_manager']['playlist_generator']['playlist_uri'].get()


class PlaylistGenerator:
    '''generates playlist'''

    def __init__(self,
                 playlist_uri=None,
                 **kwargs
                 ):
        self.spotify = get_spotify()
        self.spotify_history = get_spotify_history()

        # NOTE: bug with market='from_token' fails on unplayeble track -> TypeError
        self._market = None
        self._market_country_code = 'FI'

        # FIXME: from config?
        self.bad_words_in_album_names = ['christmas']

        # init empty
        self._isrc_seen = set()
        self._uris_seen = set()

        # get playlist
        if playlist_uri is None:
            playlist_uri = _get_playlist_uri_from_config()
        playlist_uri_type, playlist_uri_id = spotipy.convert.from_uri(playlist_uri)
        self.playlist = self.spotify.playlist(playlist_uri_id, market=self._market)
        self.playlist_snapshot_id = self.playlist.snapshot_id

        # defaults
        self.playlist_name = '< g e n e r a t e d >'
        # NOTE: not None -> get updated. '' -> fails
        self.playlist_description = '<empty>'
        # for debugging
        self.dry_run = False
        #
        self.randomize = False

        self.looper_target_count = 500
        self.looper_max_tries = 5000

        # FIXME: move to Sources class
        # TODO: use PriorityQueue or something
        self.sources_queue = collections.deque()

    # FIXME: move to Sources class
    def add_source(self, source):
        self.sources_queue.append(source)

    # FIXME: move to Sources class
    def sources_queue_generator(self):
        while True:
            try:
                yield from self.sources_queue.popleft()
            except IndexError:
                break

    def generate(self):
        self.looper()
        self.commit()
        # FIXME: continue

    def looper(self):

        track_ids_to_playlist = list()
        # logger.debug('sources: %s', self._sources)
        # sources = itertools.chain.from_iterable(self.sources_queue)
        sources = self.sources_queue_generator()

        for counter, track in enumerate(sources):
            logger.debug('counter: %i, tracks: %i, sources: %i',
                         counter,
                         len(track_ids_to_playlist),
                         len(self.sources_queue))
            #logger.debug(type(track))
            assert isinstance(track, spotipy.model.track.FullTrack)

            if track.id in track_ids_to_playlist:
                logger.debug('%s: already added', track.id)

            if self.is_track_ok_to_add(track):
                # printer.print_track(track)
                track_ids_to_playlist.append(track.id)
                logger.debug('%s: added', track.id)

            if len(track_ids_to_playlist) >= self.looper_target_count:
                logger.info('we have enough tracks to add')
                break

            # safety
            if counter > self.looper_max_tries:
                logger.info('we have tried too many tracks, breaking loop')
                break

        self.track_ids_to_playlist = track_ids_to_playlist
        logger.info(f'{len(track_ids_to_playlist)} tracks to add')

    def commit(self):
        track_ids_to_playlist = self.track_ids_to_playlist
        if not self.dry_run:
            if len(track_ids_to_playlist) > 0:
                self.playlist_clear()
                self.playlist_tracks_add(track_ids_to_playlist)
                self.playlist_details_update()
            else:
                logger.info('try something else?')
        else:
            logger.info('dry_run is True, not committing')
        logger.info('done')

    def generate_playlist_from_uris(self,
                                    uris: list,
                                    **kwargs):
        expander_params = {key: value for key, value in kwargs.items() if key.startswith('expand')}
        # FIXME: maybe we should use Options
        self.dry_run = kwargs.get('dry_run', True)
        self.randomize = kwargs.get('randomize', False)
        items = self.expand_uris(uris)
        if self.randomize:
            logger.debug('randomize is True, so shuffling uris')
            random.shuffle(items)
        for item in items:
            self.add_source(self.expander(item, **expander_params))
        self.playlist_description = f'source: {uris}'
        self.generate()

    def generate_playlist_from_search(self,
                                      query_type: str,
                                      query: str,
                                      **kwargs):
        expander_params = {key: value for key, value in kwargs.items() if key.startswith('expand')}
        self.dry_run = kwargs.get('dry_run', True)
        s = self.iterate_search(query_type=query_type, query=query)
        e = self.expander(s, **expander_params)
        self.add_source(e)
        self.playlist_description = f'source: search {query_type} "{query}"'
        self.generate()

    def generate_playlist_from_recommendations(self,
                                               seed_artist_uris: list = None,
                                               seed_track_uris: list = None,
                                               seed_genres: list = None,
                                               call_times: int = 1,
                                               recommendation_attributes: dict = None,
                                               **kwargs):
        '''generate playlist from recommendations'''

        self.dry_run = kwargs.get('dry_run', True)

        seed_artist_ids = list()
        if seed_artist_uris is not None:
            for artist in self.expand_uris(seed_artist_uris):
                seed_artist_ids.append(artist.id)
        seed_track_ids = list()
        if seed_track_uris is not None:
            for artist in self.expand_uris(seed_track_uris):
                seed_artist_ids.append(artist.id)

        # TODO: add support attributes
        s = self.iterate_recommendations(
            seed_artist_ids=seed_artist_ids,
            seed_track_ids=seed_track_ids,
            seed_genres=seed_genres,
            call_times=call_times,
            recommendation_attributes=recommendation_attributes)
        expander_params = {key: value for key, value in kwargs.items() if key.startswith('expand')}
        e = self.expander(s, **expander_params)
        self.add_source(e)
        self.playlist_description = ', '.join((
            f'source: recommendations',
            f'{seed_artist_uris}',
            f'{seed_track_uris}',
            f'{seed_genres}'))
        print(self.playlist_description)
        self.generate()

    def is_track_ok_to_add(self, track):
        if self.is_track_isrc_already_added(track):
            logger.debug(f'{track.id}: isrc already added')
            return False
        elif self.is_track_already_played(track):
            logger.debug(f'{track.id}: already played')
            return False
        elif self.is_track_isrc_already_played(track):
            logger.debug(f'{track.id}: isrc already played')
            return False
        elif not self.is_track_playeable(track):
            logger.debug(f'{track.id}: not playeable')
            return False
        elif not self.is_track_on_market(track, self._market_country_code):
            logger.debug(f'{track.id}: is not available on {self._market_country_code}')
            return False
        elif not self.is_track_album_name_good(track):
            logger.debug(f'{track.id}: album name "{track.album.name}" not good')
            return False
        else:
            return True

    def is_track_already_played(self, track):
        if self.spotify_history.count_by_track_id(track.uri) > 0:
            return True
        else:
            return False

    def is_track_isrc_already_played(self, track):
        isrc = track.external_ids.get('isrc')
        if isrc is None:
            return False
        if self.spotify_history.count_by_track_isrc(isrc) > 0:
            return True
        else:
            return False

    def is_track_isrc_already_added(self, track):
        isrc = track.external_ids.get('isrc')
        if isrc is None:
            return False
        elif isrc in self._isrc_seen:
            return True
        else:
            self._isrc_seen.add(isrc)
            return False

    def is_track_playeable(self, track):
        if track.is_playable is None:
            # should log warning or something
            return True
        else:
            return track.is_playable

    def is_track_on_market(self, track, market):
        markets = track.available_markets
        if markets is None:
            # hjum?
            return True
        elif market in markets:
            return True
        else:
            return False

    def is_track_album_name_good(self, track):
        if any(bad in track.album.name.lower() for bad in self.bad_words_in_album_names):
            return False
        else:
            return True

    def is_uri_already_seen(self, uri):
        if uri in self._uris_seen:
            logger.debug('%s is already seen', uri)
            return True
        else:
            self._uris_seen.add(uri)
            return False

    # playlist modify methods

    def playlist_clear(self):
        self.spotify.playlist_tracks_replace(self.playlist.id, [])

    def playlist_reload(self):
        self.playlist = self.spotify.playlist(self.playlist.id)

    def playlist_tracks_add(self, track_ids):
        chunks = self.list_to_chunks(track_ids, 100)
        for chunk in chunks:
            self.playlist_snapshot_id = self.spotify.playlist_tracks_add(self.playlist.id, chunk)

    def playlist_details_update(self):
        if self.playlist_description is None:
            logger.warning('playlist description is None')
        self.spotify.playlist_change_details(
            self.playlist.id,
            name=self.playlist_name,
            description=self.playlist_description)

    # util functions
    def list_to_chunks(self, l: list, n: int):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    # generators

    def artist_albums(self, artist_id: str):
        '''artist all albumns'''

        # NOTE: 'album', 'single', 'appears_on', 'compilation'
        include_album_groups = ['album', 'single', 'compilation']

        paging = self.spotify.artist_albums(
            artist_id,
            include_groups=include_album_groups,
            market=self._market)

        yield from self.spotify.items_from_paging(paging)

    # FIXME: rename
    def iterate_artist_all_tracks(self, artist_id: str):
        '''artist all tracks'''
        for album in self.artist_albums(artist_id):
            yield from self.iterate_album_tracks(album.id)

    # FIXME: rename
    def iterate_album_tracks(self, album_id):
        paging = self.spotify.album_tracks(album_id,
                                           market=self._market,
                                           limit=50)
        for simple_track in self.spotify.items_from_paging(paging):
            yield self.spotify.track(simple_track.id, market=self._market)

    def iterate_recommendations(self,
                                seed_artist_ids: list = None,
                                seed_track_ids: list = None,
                                seed_genres: list = None,
                                call_times: int = 1,
                                recommendation_attributes: dict = None
                                ):
        if recommendation_attributes is None:
            recommendation_attributes = {}

        # FIXME: call_times is hack
        # NOTE: calling n times is not usefull cos recommendatios is always pretty same on same seed
        for n in range(call_times):
            # NOTE: market=None gives many unplayeble tracks
            recommendations = self.spotify.recommendations(
                                                    artist_ids=seed_artist_ids,
                                                    track_ids=seed_track_ids,
                                                    genres=seed_genres,
                                                    market=self._market_country_code,
                                                    limit=100,
                                                    **recommendation_attributes)

            for seed in recommendations.seeds:
                logger.debug(seed)
            yield from recommendations.tracks

    # FIXME: not used?
    def iterate_related_artists_all_tracks(self, artist_id):
        for artist in self.spotify.artist_related_artists(artist_id):
            yield from self.iterate_artist_all_tracks(artist.id)

    # FIXME: rename
    def iterate_related_artists(self, artist_id):
        yield from self.spotify.artist_related_artists(artist_id)

    # FIXME: rename
    def iterate_search(self, query_type: str, query: str):
        '''search'''
        search = self.spotify.search(query=query,
                                     types=[query_type],
                                     limit=50,
                                     market=self._market)
        paging = search[0]
        for count, item in enumerate(self.spotify.items_from_paging(paging), start=1):
            # NOTE: item can me track, album, artist, playlist ...
            yield item

    # FIXME: rename
    def iterate_playlist_all_tracks(self,
                                    playlist_id: str):
        playlist = self.spotify.playlist(playlist_id=playlist_id, market=None)
        playlist_tracks = self.spotify.iterate_items_from_paging(playlist.tracks)
        for playlist_track in playlist_tracks:
            yield playlist_track.track

    # FIXME: not used, remove
    def track_expand(self, track,
                     expand_album: bool = False,
                     expand_artist: bool = False):
        if expand_album:
            for track in self.iterate_album_tracks(track.album.id):
                yield track
        elif expand_artist:
            for artist in track.artists:
                for track in self.iterate_artist_all_tracks(artist.id):
                    yield track
        else:
            yield track

    # FIXME: not used, remove
    def artist_expand(self, artist,
                      expand_albums: bool = False,
                      expand_top_tracks: bool = False):
        if expand_albums:
            # FIXME: yield albumns?
            for track in self.iterate_artist_all_tracks(artist.id):
                yield track
        elif expand_top_tracks:
            # FIXME: move to method? and add support different countries
            yield from self.spotify.artist_top_tracks(artist.id,
                                                      country=self._market_country_code)
        else:
            return

    # FIXME: this was very stupid idea
    def expander(self, item,
                 expand_track_to_album: bool = False,
                 expand_track_to_artist: bool = False,
                 expand_artist_to_albums: bool = False,
                 expand_artist_to_top_tracks: bool = False,
                 expand_artist_to_related_artists: bool = False,
                 expand_album_to_tracks: bool = False,
                 expand_playlist_to_tracks: bool = False,
                 expand_generator_to_items: bool = False
                 ):
        logger.debug('%s', type(item))
        expander_params = {key: value for key, value in locals().items() if key.startswith('expand')}

        # generators
        if isinstance(item, types.GeneratorType):
            if expand_generator_to_items:
                for item_ in item:
                    yield from self.expander(item_, **expander_params)
            else:
                logger.warning('did not do anything with generator: %s', item)

        # modellist
        elif isinstance(item, spotipy.serialise.ModelList):
            # FIXME: add if expand_modellist_to_items:
            for item_ in item:
                yield from self.expander(item_, **expander_params)

        # track
        elif isinstance(item, spotipy.model.track.FullTrack):

            if expand_track_to_artist and expand_track_to_album:
                logger.warning('expand_track_to_artist AND expand_track_to_album')

            # FIXME: if elif else
            if expand_track_to_artist and not self.is_uri_already_seen(item.uri + '#artists'):
                # add artist as new source
                _expander_params = expander_params.copy()
                _expander_params['expand_track_to_artist'] = False
                for artist in item.artists:
                    self.add_source(
                        self.expander(
                            self.spotify.artist(artist.id),
                            **_expander_params))

            # FIXME: expand_track_to_album and expand_album_to_tracks causes infinite loop?
            elif expand_track_to_album and not self.is_uri_already_seen(item.uri + '#album'):
                _expander_params = expander_params.copy()
                _expander_params['expand_track_to_album'] = False
                yield from self.expander(self.spotify.album(item.album.id, market=self._market),
                                         **_expander_params)
            else:
                # FIXME: if we first expand and later try again, we never yield track
                if not self.is_uri_already_seen(item.uri):
                    yield item

        # artist
        elif isinstance(item, spotipy.model.artist.Artist):
            if self.is_uri_already_seen(item.uri):
                return

            if expand_artist_to_related_artists:
                # add artists as new source
                self.add_source(
                    self.expander(
                        self.iterate_related_artists(item.id),
                        **expander_params))

            # FIXME: if elif else? order?
            if expand_artist_to_albums:
                yield from self.expander(self.artist_albums(item.id),
                                         **expander_params)
            elif expand_artist_to_top_tracks:
                # FIXME: use expander
                # FIXME: move to method? and add support different countries
                yield from self.expander(
                    self.spotify.artist_top_tracks(item.id,
                                                   country=self._market_country_code),
                    **expander_params)
            else:
                # FIXME: can be sfalse alarm
                logger.warning('did not do anything with artist: %s', item.id)

        # album
        elif isinstance(item, spotipy.model.album.Album):
            if self.is_uri_already_seen(item.uri):
                return
            if expand_album_to_tracks and not self.is_uri_already_seen(item.uri + '#tracks'):
                # hopefully this and seen #tracks fixes infitine loop
                # if both expand_album_to_tracks and expand_track_to_album is True
                _expander_params = expander_params.copy()
                _expander_params['expand_track_to_album'] = False
                yield from self.expander(self.iterate_album_tracks(item.id), **_expander_params)
            else:
                logger.warning('did not do anything with album: %s', item.id)

        # playlist
        elif isinstance(item, spotipy.model.playlist.Playlist):
            if self.is_uri_already_seen(item.uri):
                return
            if expand_playlist_to_tracks:
                yield from self.expander(self.iterate_playlist_all_tracks(item.id),
                                         **expander_params)
            else:
                logger.warning('did not do anything with artist: %s', item.id)
        else:
            logger.warning('not yet supported: %s', type(item))
            raise Exception()

    # FIXME: better name?
    def expand_uris(self, uris: list):
        items = list()
        for uri in uris:
            uri_type, uri_id = spotipy.convert.from_uri(uri)
            logger.debug('%s: %s', uri_type, uri_id)
            if uri_type == 'artist':
                items.append(self.spotify.artist(uri_id))
            elif uri_type == 'album':
                items.append(self.spotify.album(uri_id, market=self._market))
            elif uri_type == 'track':
                items.append(self.spotify.track(uri_id, market=self._market))
            elif uri_type == 'playlist':
                items.append(self.spotify.playlist(uri_id, market=self._market))
            else:
                logger.warning('unsupported uri: %s (%s, %s)', uri, uri_type, uri_id)
        return items

# END
