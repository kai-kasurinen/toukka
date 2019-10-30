#
#

from typing import Generator

import logging
import pprint
import itertools
import types
import collections
import random

import autologging

from options import Options

import spotipy.convert
import spotipy.serialise
import spotipy.model.track
import spotipy.model.artist
import spotipy.model.playlist
import spotipy.model.album

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history
from toukka.sopiva.spotify.printer import first as printer

from .playlist import Playlist


class SourcesQueue:
    def __init__(self):
        self.sources_queue = collections.deque()

    # FIXME: move to Sources class
    def add(self, source):
        self.sources_queue.append(source)

    # FIXME: move to Sources class
    def generator(self):
        while True:
            try:
                yield from self.sources_queue.popleft()
            except IndexError:
                break

    def __len__(self):
        return len(self.sources_queue)


@autologging.traced
@autologging.logged
class PlaylistGenerator:
    '''generates playlist'''

    options = Options(
        dry_run=False,
        randomize=False,
        looper_target_count=500,
        looper_max_tries=5000,
        expand_track_to_album=False,
        expand_track_to_artist=False,
        expand_artist_to_albums=False,
        expand_artist_to_top_tracks=False,
        expand_artist_to_related_artists=False,
        expand_album_to_tracks=False,
        expand_playlist_to_tracks=False,
        expand_generator_to_items=False
    )

    def __init__(self,
                 playlist_uri=None,
                 **kwargs
                 ):
        self.options = PlaylistGenerator.options.push(kwargs)

        self.spotify = get_spotify()
        self.spotify_history = get_spotify_history()

        # NOTE: bug with market='from_token' fails on unplayeble track -> TypeError
        # NOTE: bug is fixed, so clear this mess
        self._market = None
        self._market_country_code = 'FI'

        # FIXME: from config?
        self.bad_words_in_album_names = ['christmas']

        # init empty
        self._isrc_seen = set()
        self._uris_seen = set()

        self.playlist = Playlist(uri=playlist_uri, spotify=self.spotify)
        self.sources = SourcesQueue()

        # FIXME: remove
        self.__log.setLevel(logging.DEBUG)

    def generate(self):
        self.looper()
        self.commit()

    def looper(self):

        track_ids_to_playlist = list()

        for counter, track in enumerate(self.sources.generator()):

            self.__log.debug(
                'counter: %i, tracks: %i, sources: %i',
                counter,
                len(track_ids_to_playlist),
                len(self.sources))

            assert isinstance(track, spotipy.model.track.FullTrack)

            if track.id in track_ids_to_playlist:
                self.__log.debug('%s: already added', track.id)

            if self.is_track_ok_to_add(track):
                # printer.print_track(track)
                track_ids_to_playlist.append(track.id)
                self.__log.debug('%s: added', track.id)

            if len(track_ids_to_playlist) >= self.options.looper_target_count:
                self.__log.info('we have enough tracks to add')
                break

            # safety
            if counter > self.options.looper_max_tries:
                self.__log.info('we have tried too many tracks, breaking loop')
                break

        self.track_ids_to_playlist = track_ids_to_playlist
        self.__log.info(f'{len(track_ids_to_playlist)} tracks to add')

    # TODO: split and move to Playlist
    def commit(self):
        track_ids_to_playlist = self.track_ids_to_playlist
        if not self.options.dry_run:
            if len(track_ids_to_playlist) > 0:
                self.playlist.clear()
                self.playlist.tracks_add(track_ids_to_playlist)
                self.playlist.details_update()
            else:
                self.__log.info('try something else?')
        else:
            self.__log.info('dry_run is True, not committing')
        self.__log.info('done')

    def generate_playlist_from_uris(self,
                                    uris: list,
                                    **kwargs):
        self.options.update(kwargs)
        self.__log.debug(self.options)
        items = self.uris_to_items(uris)
        if self.options.randomize:
            self.__log.debug('shuffling uris')
            random.shuffle(items)
        for item in items:
            self.sources.add(self.expander(item))
        self.playlist.description = f'source: {", ".join(uris)}'
        self.generate()

    def generate_playlist_from_search(self,
                                      query_type: str,
                                      query: str,
                                      **kwargs):
        self.options.update(kwargs)
        s = self.search_generator(query_type=query_type, query=query)
        e = self.expander(s)
        self.sources.add(e)
        self.playlist.description = f'source: search {query_type} "{query}"'
        self.generate()

    def generate_playlist_from_recommendations(self,
                                               seed_artist_uris: list = None,
                                               seed_track_uris: list = None,
                                               seed_genres: list = None,
                                               recommendation_attributes: dict = None,
                                               **kwargs):
        '''generate playlist from recommendations'''
        self.options.update(kwargs)

        seed_artist_ids = list()
        if seed_artist_uris is not None:
            for artist in self.uris_to_items(seed_artist_uris):
                seed_artist_ids.append(artist.id)
        seed_track_ids = list()
        if seed_track_uris is not None:
            for artist in self.uris_to_items(seed_track_uris):
                seed_artist_ids.append(artist.id)

        # TODO: add support attributes
        s = self.recommendations_generator(
            seed_artist_ids=seed_artist_ids,
            seed_track_ids=seed_track_ids,
            seed_genres=seed_genres,
            recommendation_attributes=recommendation_attributes)
        e = self.expander(s)
        self.sources.add(e)
        self.playlist.description = ', '.join((
            f'source: recommendations',
            f'{seed_artist_uris}',
            f'{seed_track_uris}',
            f'{seed_genres}'))
        print(self.playlist.description)
        self.generate()

    def is_track_ok_to_add(self, track):
        if self.is_track_isrc_already_added(track):
            self.__log.debug(f'{track.id}: isrc already added')
            return False
        elif self.is_track_already_played(track):
            self.__log.debug(f'{track.id}: already played')
            return False
        elif self.is_track_isrc_already_played(track):
            self.__log.debug(f'{track.id}: isrc already played')
            return False
        elif not self.is_track_playeable(track):
            self.__log.debug(f'{track.id}: not playeable')
            return False
        elif not self.is_track_on_market(track, self._market_country_code):
            self.__log.debug(f'{track.id}: is not available on {self._market_country_code}')
            return False
        elif not self.is_track_album_name_good(track):
            self.__log.debug(f'{track.id}: album name "{track.album.name}" not good')
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
            self.__log.debug('%s is already seen', uri)
            return True
        else:
            self._uris_seen.add(uri)
            return False

    # generators

    def artist_albums_generator(self,
                                artist_id: str
                                ) -> Generator[spotipy.model.album.full.FullAlbum, None, None]:
        # NOTE: 'album', 'single', 'appears_on', 'compilation'
        include_album_groups = ['album', 'single', 'compilation']
        paging = self.spotify.artist_albums(
            artist_id,
            include_groups=include_album_groups,
            market=self._market)
        yield from self.spotify.all_items_from_paging(paging)

    def artist_all_tracks_generator(self,
                                    artist_id: str
                                    ) -> Generator[spotipy.model.track.FullTrack, None, None]:
        for album in self.artist_albums_generator(artist_id):
            yield from self.album_tracks_generator(album.id)

    def artist_top_tracks_generator(self,
                                    artist_id: str
                                    ) -> Generator[spotipy.model.track.FullTrack, None, None]:
        yield from self.spotify.artist_top_tracks(item.id,
                                                  country=self._market_country_code)

    def album_tracks_generator(self,
                               album_id
                               ) -> Generator[spotipy.model.track.FullTrack, None, None]:
        paging = self.spotify.album_tracks(
            album_id,
            market=self._market,
            limit=50)
        for simple_track in self.spotify.all_items_from_paging(paging):
            yield self.spotify.track(simple_track.id, market=self._market)

    def recommendations_generator(self,
                                  seed_artist_ids: list = None,
                                  seed_track_ids: list = None,
                                  seed_genres: list = None,
                                  recommendation_attributes: dict = None
                                  ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        if recommendation_attributes is None:
            recommendation_attributes = {}

        # NOTE: market=None gives many unplayeble tracks
        recommendations = self.spotify.recommendations(
            artist_ids=seed_artist_ids,
            track_ids=seed_track_ids,
            genres=seed_genres,
            market=self._market_country_code,
            limit=100,
            **recommendation_attributes)

        for seed in recommendations.seeds:
            self.__log.debug(seed)
        yield from recommendations.tracks

    # FIXME: not used?
    def related_artists_all_tracks_generator(self, artist_id
                                             ) -> Generator[spotipy.model.track.FullTrack, None, None]:
        for artist in self.spotify.artist_related_artists(artist_id):
            yield from self.artist_all_tracks_generator(artist.id)

    def related_artists_generator(self, artist_id):
        yield from self.spotify.artist_related_artists(artist_id)

    def search_generator(self, query_type: str, query: str):
        search = self.spotify.search(query=query,
                                     types=[query_type],
                                     limit=50,
                                     market=self._market)
        paging = search[0]
        for item in self.spotify.all_items_from_paging(paging):
            # NOTE: item can me track, album, artist, playlist ...
            yield item

    def playlist_all_tracks_generator(self,
                                      playlist_id: str
                                      ) -> Generator[spotipy.model.track.FullTrack, None, None]:
        playlist = self.spotify.playlist(playlist_id=playlist_id, market=None)
        playlist_tracks = self.spotify.all_items_from_paging(playlist.tracks)
        for playlist_track in playlist_tracks:
            yield playlist_track.track

    def randomizer(self, generator):
        if self.options.randomize:
            self.__log.debug('randomizing %s', generator)
            yield from scramble_generator(generator, 100)
        else:
            yield from generator

    # FIXME: rename and use single dispatch method
    def expander(self, item, **kwargs):
        opts = self.options.push(kwargs)
        self.__log.debug('%s', type(item))

        if isinstance(item, types.GeneratorType):
            yield from self.expand_generator(item, **opts)
        elif isinstance(item, autologging._GeneratorIteratorTracingProxy):
            yield from self.expand_generator(item, **opts)
        elif isinstance(item, spotipy.serialise.ModelList):
            yield from self.expand_modellist(item, **opts)
        elif isinstance(item, spotipy.model.track.FullTrack):
            yield from self.expand_track(item, **opts)
        elif isinstance(item, spotipy.model.artist.Artist):
            yield from self.expand_artist(item, **opts)
        elif isinstance(item, spotipy.model.album.Album):
            yield from self.expand_album(item, **opts)
        elif isinstance(item, spotipy.model.playlist.Playlist):
            yield from self.expand_playlist(item, **opts)
        else:
            self.__log.warning('not yet supported: %s', type(item))
            raise Exception()

    def expand_generator(self,
                         item: types.GeneratorType,
                         **kwargs):
        opts = self.options.push(kwargs)
        if opts.expand_generator_to_items:
            for item_ in item:
                yield from self.expander(item_, **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    # FIXME: where this is used?
    def expand_modellist(self,
                         item: spotipy.serialise.ModelList,
                         **kwargs):
        opts = self.options.push(kwargs)
        if opts.expand_modellist_to_items:
            for item_ in item:
                yield from self.expander(item_, **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    def expand_track(self,
                     item: spotipy.model.track.FullTrack,
                     **kwargs):
        opts = self.options.push(kwargs)

        # FIXME: move?
        if opts.expand_track_to_artist and opts.expand_track_to_album:
            self.__log.warning('expand_track_to_artist AND expand_track_to_album')

        # FIXME: if elif else
        if opts.expand_track_to_artist and not self.is_uri_already_seen(item.uri + '#artists'):
            opts.set(expand_track_to_artist=False)
            for artist in item.artists:
                self.sources.add(
                    self.expander(
                        self.spotify.artist(artist.id),
                        **opts))

        elif opts.expand_track_to_album and not self.is_uri_already_seen(item.uri + '#album'):
            opts.set(expand_track_to_album=False)
            yield from self.expander(
                self.spotify.album(item.album.id, market=self._market),
                **opts)
        else:
            # FIXME: if we first expand and later try again, we never yield track
            if not self.is_uri_already_seen(item.uri):
                yield item

    def expand_artist(self,
                      item: spotipy.model.artist.FullArtist,
                      **kwargs):
        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(item.uri):
            return

        if opts.expand_artist_to_related_artists:
            # add artists as new source
            self.sources.add(
                self.expander(
                    self.related_artists_generator(item.id),
                    **opts))
        # FIXME: if elif else? order?
        if opts.expand_artist_to_albums:
            yield from self.expander(
                self.artist_albums_generator(item.id),
                **opts)
        elif opts.expand_artist_to_top_tracks:
            yield from self.expander(
                self.artist_top_tracks_generator(item.id),
                **opts)
        else:
            # FIXME: can be false alarm
            self.__log.warning('did not do anything with: %s', item)

    def expand_album(self,
                     item: spotipy.model.album.full.FullAlbum,
                     **kwargs):
        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(item.uri):
            return
        if opts.expand_album_to_tracks and not self.is_uri_already_seen(item.uri + '#tracks'):
            opts.set(expand_track_to_album=False)
            yield from self.expander(
                self.album_tracks_generator(item.id),
                **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    def expand_playlist(self,
                        item: spotipy.model.playlist.Playlist,
                        **kwargs):
        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(item.uri):
            return
        elif opts.expand_playlist_to_tracks:
            yield from self.expander(
                self.randomizer(
                    self.playlist_all_tracks_generator(item.id)),
                **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    def uris_to_items(self, uris: list):
        items = list()
        for uri in uris:
            uri_type, uri_id = spotipy.convert.from_uri(uri)
            self.__log.debug('%s: %s', uri_type, uri_id)
            if uri_type == 'artist':
                items.append(self.spotify.artist(uri_id))
            elif uri_type == 'album':
                items.append(self.spotify.album(uri_id, market=self._market))
            elif uri_type == 'track':
                items.append(self.spotify.track(uri_id, market=self._market))
            elif uri_type == 'playlist':
                items.append(self.spotify.playlist(uri_id, market=self._market))
            else:
                self.__log.warning('unsupported uri: %s (%s, %s)', uri, uri_type, uri_id)
        return items

# END OF CLASS

# util functions


# source: https://stackoverflow.com/questions/21187131/how-to-use-random-shuffle-on-a-generator-python
# modified
def shuffle_generator(generator, buffer_size):
    while True:
        buffer = list(itertools.islice(generator, buffer_size))
        if len(buffer) == 0:
            break
        random.shuffle(buffer)
        for item in buffer:
            yield item


# source: https://stackoverflow.com/questions/21187131/how-to-use-random-shuffle-on-a-generator-python
# modified
def scramble_generator(generator, buffer_size):
    buf = []
    i = iter(generator)
    while True:
        try:
            e = next(i)
            buf.append(e)
            if len(buf) >= buffer_size:
                choice = random.randint(0, len(buf)-1)
                buf[-1], buf[choice] = buf[choice], buf[-1]
                yield buf.pop()
        except StopIteration:
            random.shuffle(buf)
            yield from buf
            return

# END
