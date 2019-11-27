#
#

from typing import List, Set, Generator, Union, Any, Dict, cast

import logging
import pprint
import types
import random

# import autologging
import enlighten

from options import Options

import spotipy.convert
import spotipy.serialise
import spotipy.model.track
import spotipy.model.artist
import spotipy.model.playlist
import spotipy.model.album

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer

from .playlist import Playlist
from .sources_queue import SourcesQueue
from .track_filter import TrackFilter
from .util import scramble_generator
from .progress_bar import ProgressBars


# @autologging.traced
# @autologging.logged
class PlaylistGenerator:
    '''generates playlist'''

    def __init__(self,
                 playlist_uri: str = None,
                 **kwargs
                 ) -> None:

        # TODO: move
        options = Options(
            dry_run=False,
            progress_bar=False,
            randomize=False,
            looper_target_count=500,
            looper_max_tries=5000,
            expand_track_to_album=False,
            expand_track_to_artists=False,
            expand_track_to_recommendations=False,
            expand_artist_to_albums=False,
            expand_artist_to_top_tracks=False,
            expand_artist_to_related_artists=False,
            expand_artist_to_recommendations=False,
            expand_album_to_tracks=False,
            expand_album_to_artists=False,
            expand_playlist_to_tracks=False,
            expand_generator_to_items=True
        )

        self.options = options.push(kwargs)

        self.spotify = get_spotify()
        self.user_country = self.spotify.current_user().country
        # disabling track relinking
        self.market = None

        # init empty
        self._uris_seen: Set[str] = set()
        # FIXME: use orderedset
        self.track_ids_to_playlist: List[str] = list()

        self.playlist = Playlist(uri=playlist_uri, spotify=self.spotify)
        self.sources = SourcesQueue()
        self.track_filter = TrackFilter(
            spotify=self.spotify,
            track_ids_to_playlist=self.track_ids_to_playlist,
            user_country=self.user_country)

        # FIXME: do something (emulates what autologging provides
        self.__log = logging.getLogger(__name__)
        # FIXME: remove
        self.__log.setLevel(logging.DEBUG)
        self.__log.debug('initialized %s', self)
        self.__log.debug('options %s', self.options)

    def generate(self, **kwargs) -> None:
        opts = self.options.push(kwargs)
        self.looper(**opts)
        self.commit(**opts)

    def looper(self, **kwargs) -> None:
        opts = self.options.push(kwargs)

        # FIXME: move?
        progress_bars = ProgressBars(enabled=opts.progress_bar)
        # NOTE: order means something
        progress_tracks = progress_bars.progress_bar_for_tracks(opts.looper_target_count)
        progress_looper = progress_bars.progress_bar_for_loops(opts.looper_max_tries)

        sources = self.sources.generator()

        # wanted type
        track: spotipy.model.track.Track

        for counter, track in enumerate(sources):

            self.__log.debug(
                'counter: %i, tracks: %i, sources: %i',
                counter,
                len(self.track_ids_to_playlist),
                len(self.sources))

            progress_looper.update()

            # TODO: remove
            # actually we do not care as long track.id is usable
            if not isinstance(track, spotipy.model.track.Track):
                raise Exception(f'wrong type received: {type(track)}')

            # shortcut, for speedup things
            if self.track_filter.is_track_already_played(track):
                self.__log.debug('track:%s: already played', track.id)
                continue

            if self.track_filter.is_track_ok_to_add(track):
                self.track_ids_to_playlist.append(track.id)
                self.__log.debug('track:%s: added', track.id)
                progress_tracks.update()

            if len(self.track_ids_to_playlist) >= opts.looper_target_count:
                self.__log.info('we have enough tracks to add (target count)')
                break

            # playlist can contains only ~10000 tracks
            # (actually 11000 and then 500 ISE)
            if len(self.track_ids_to_playlist) >= 10000:
                self.__log.info('we have enough tracks to add (playlist max)')
                break

            # safety
            if counter >= opts.looper_max_tries:
                self.__log.info('we have tried too many tracks')
                break

        progress_bars.stop()

        self.__log.info(f'{len(self.track_ids_to_playlist)} tracks to add')

    # TODO: split and move to Playlist
    def commit(self, **kwargs) -> None:
        opts = self.options.push(kwargs)

        track_ids_to_playlist = self.track_ids_to_playlist
        if not opts.dry_run:
            if len(track_ids_to_playlist) > 0:
                self.playlist.clear()
                self.playlist.tracks_add(track_ids_to_playlist)
                self.playlist.details_update()
            else:
                self.__log.info('try something else?')
        else:
            self.__log.info('dry_run is True, not committing')
        self.__log.info('done')

    def generate_from_uris(self,
                           uris: List,
                           **kwargs) -> None:
        opts = self.options.push(kwargs)
        self.__log.debug('method options: %s', opts)

        if opts.randomize:
            self.__log.debug('shuffling uris')
            random.shuffle(uris)
        for uri in uris:
            self.sources.add(self.expand_uri(uri, **opts))
        self.playlist.description = f'source: {", ".join(uris)}'
        self.generate(**opts)

    def generate_from_search(self,
                             query_type: str,
                             query: str,
                             **kwargs) -> None:
        opts = self.options.push(kwargs)
        self.__log.debug('method options: %s', opts)

        s = self.search_generator(query_type=query_type, query=query)
        e = self.expander(self.randomizer(s, **opts), **opts)
        self.sources.add(e)
        self.playlist.description = f'source: search {query_type} "{query}"'
        self.generate(**opts)

    def generate_from_recommendations(self,
                                      seed_artist_uris: List = None,
                                      seed_track_uris: List = None,
                                      seed_genres: List = None,
                                      seed_attributes: Dict = None,
                                      **kwargs) -> None:
        opts = self.options.push(kwargs)
        self.__log.debug('method options: %s', opts)

        seed_artist_ids: List[str] = list()
        if seed_artist_uris is not None:
            for artist in self.uris_to_items(seed_artist_uris):
                seed_artist_ids.append(artist.id)
        seed_track_ids: List[str] = list()
        if seed_track_uris is not None:
            for artist in self.uris_to_items(seed_track_uris):
                seed_artist_ids.append(artist.id)

        # TODO: move seed_attributes validation here?

        s = self.recommendations_generator(
            seed_artist_ids=seed_artist_ids,
            seed_track_ids=seed_track_ids,
            seed_genres=seed_genres,
            seed_attributes=seed_attributes)
        e = self.expander(self.randomizer(s), **opts)
        self.sources.add(e)
        self.playlist.description = ', '.join((
            f'source: recommendations',
            f'{seed_artist_uris}',
            f'{seed_track_uris}',
            f'{seed_genres}'))
        print(self.playlist.description)
        self.generate(**opts)

    # TODO: split check and add
    def is_uri_already_seen(self, uri: str, debug=False) -> bool:
        if uri in self._uris_seen:
            if debug:
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
            limit=50,
            market=self.market)
        for album in self.spotify.all_items_from_paging(paging):
            # speed up things
            if self.user_country not in album.available_markets:
                self.__log.debug('album:%s: is not available %s', album.id, self.user_country)
                continue
            yield album

    def artist_top_tracks_generator(self,
                                    artist_id: str
                                    ) -> Generator[spotipy.model.track.FullTrack, None, None]:
        yield from self.spotify.artist_top_tracks(artist_id,
                                                  country=self.user_country)

    def album_tracks_generator(self,
                               album_id: str
                               ) -> Generator[spotipy.model.track.SimpleTrack, None, None]:
        paging = self.spotify.album_tracks(
            album_id,
            market=self.market,
            limit=50)
        # NOTE: yield SimpleTracks
        yield from self.spotify.all_items_from_paging(paging)

    def recommendations_generator(self,
                                  seed_artist_ids: List = None,
                                  seed_track_ids: List = None,
                                  seed_genres: List = None,
                                  seed_attributes: Dict = None
                                  ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        if seed_attributes is None:
            seed_attributes = {}

        # NOTE: market=None may return lot of unplayable tracks
        recommendations = self.spotify.recommendations(
            artist_ids=seed_artist_ids,
            track_ids=seed_track_ids,
            genres=seed_genres,
            market=self.market,
            limit=100,
            **seed_attributes)

        for seed in recommendations.seeds:
            self.__log.debug(seed)
        yield from recommendations.tracks

    def related_artists_generator(self, artist_id: str
                                  ) -> Generator[spotipy.model.artist.FullArtist, None, None]:
        yield from self.spotify.artist_related_artists(artist_id)

    def search_generator(self,
                         query_type: str,
                         query: str
                         ) -> Generator[
                             Union[spotipy.model.track.FullTrack,
                                   spotipy.model.album.SimpleAlbum,
                                   spotipy.model.artist.FullArtist,
                                   spotipy.model.playlist.SimplePlaylist],
                             None, None]:

        search = self.spotify.search(query=query,
                                     types=[query_type],
                                     limit=50,
                                     market=self.market)
        # FIXME: handle all types not just one
        paging = search[0]
        for item in self.spotify.all_items_from_paging(paging):
            # NOTE: item can me track, album, artist, playlist ...
            yield item

    def playlist_all_tracks_generator(self,
                                      playlist_id: str
                                      ) -> Generator[spotipy.model.track.FullTrack, None, None]:
        paging = self.spotify.playlist_tracks(playlist_id=playlist_id,
                                              limit=100,
                                              market=self.market)
        for playlist_track in self.spotify.all_items_from_paging(paging):
            if playlist_track.track is not None and not playlist_track.is_local:
                yield playlist_track.track

    def randomizer(self, generator: Generator, **kwargs) -> Generator[Any, None, None]:
        opts = self.options.push(kwargs)
        if opts.randomize:
            self.__log.debug('randomizing %s', generator)
            yield from scramble_generator(generator, 100)
        else:
            yield from generator

    # TODO: use single dispatch method
    def expander(self, item, **kwargs
                 ) -> Generator[spotipy.model.track.Track, None, None]:
        opts = self.options.push(kwargs)
        # self.__log.debug('%s', type(item))
        if isinstance(item, types.GeneratorType):
            yield from self.expander_generator(item, **opts)
        # elif isinstance(item, autologging._GeneratorIteratorTracingProxy):
        #     yield from self.expander_generator(item, **opts)
        elif isinstance(item, spotipy.serialise.ModelList):
            yield from self.expander_modellist(item, **opts)
        elif isinstance(item, spotipy.model.track.Track):
            yield from self.expander_track(item, **opts)
        # elif isinstance(item, spotipy.model.track.FullTrack):
        #    yield from self.expander_track(item, **opts)
        # elif isinstance(item, spotipy.model.track.SimpleTrack):
        #    yield from self.expander_simple_track(item, **opts)
        elif isinstance(item, spotipy.model.artist.Artist):
            yield from self.expander_artist(item, **opts)
        elif isinstance(item, spotipy.model.album.Album):
            yield from self.expander_album(item, **opts)
        elif isinstance(item, spotipy.model.playlist.Playlist):
            yield from self.expander_playlist(item, **opts)
        else:
            raise Exception('not yet supported: %s', type(item))

    def expander_generator(self,
                           item: types.GeneratorType,
                           **kwargs) -> Generator[Any, None, None]:
        opts = self.options.push(kwargs)
        if opts.expand_generator_to_items:
            for item_ in item:
                yield from self.expander(item_, **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    # FIXME: is used?
    def expander_modellist(self,
                           item: spotipy.serialise.ModelList,
                           **kwargs) -> Generator[Any, None, None]:
        opts = self.options.push(kwargs)
        if opts.expand_modellist_to_items:
            for item_ in item:
                yield from self.expander(item_, **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    def expander_track(self,
                       item: spotipy.model.track.Track,
                       **kwargs
                       ) -> Generator[spotipy.model.track.Track, None, None]:
        opts = self.options.push(kwargs)
        self.__log.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False

        # add as new source
        if opts.expand_track_to_artists:
            self.add_track_artists_as_source(item, **opts)
            did = True
        # add as new source
        if opts.expand_track_to_recommendations:
            self.add_track_recommendations_as_source(item, **opts)
            did = True
        # yields tracks
        if opts.expand_track_to_album:
            yield from self.expand_track_to_album(item, **opts)
            did = True
        # and finally use track if not seen
        if not self.is_uri_already_seen(item.uri):
            yield item
            did = True
        # nice hack
        if not did:
            self.__log.warning('did not do anything with: %s', item.uri)

    def expand_track_to_album(self,
                              track: spotipy.model.track.Track,
                              **kwargs) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(track.uri + '#album'):
            return
        # only FullTrack has album property
        if not isinstance(track, spotipy.model.track.FullTrack):
            track = self.spotify.track(track.id, market=None)
        # makes mypy happy
        track = cast(spotipy.model.track.FullTrack, track)

        # set expand_track_to_album option False, so we dont hit again
        opts.set(expand_track_to_album=False)
        e = self.expander(
            self.spotify.album(track.album.id, market=self.market), **opts)
        yield from e

    def add_artist_as_source(self,
                             artist: spotipy.model.artist.Artist,
                             **kwargs) -> None:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(artist.uri + '#source'):
            return
        e = self.expander(self.spotify.artist(artist.id), **opts)
        self.sources.add(e)

    def add_track_recommendations_as_source(self,
                                            track: spotipy.model.track.Track,
                                            **kwargs) -> None:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(track.uri + '#recommendations'):
            return
        e = self.expander(self.randomizer(
                self.recommendations_generator(seed_track_ids=[track.id]),
                **opts), **opts)
        self.sources.add(e)

    def add_track_artists_as_source(self,
                                    track: spotipy.model.track.Track,
                                    **kwargs) -> None:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(track.uri + '#artists'):
            return
        # set expand_track_to_artists option to False, so we dont hit again
        # opts.set(expand_track_to_artists=False)
        for artist in track.artists:
            self.add_artist_as_source(artist, **opts)

    def add_artist_related_artists_as_source(self,
                                             artist: spotipy.model.artist.Artist,
                                             **kwargs) -> None:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(artist.uri + '#related'):
            return
        e = self.expander(self.randomizer(
                self.related_artists_generator(artist.id),
                **opts), **opts)
        self.sources.add(e)

    def add_artist_recommendations_as_source(self,
                                             artist: spotipy.model.artist.Artist,
                                             **kwargs) -> None:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(artist.uri + '#recommendations'):
            return
        e = self.expander(self.randomizer(
                self.recommendations_generator(seed_artist_ids=[artist.id]),
                **opts), **opts)
        self.sources.add(e)

    # TODO: remove, not needed
    # NOTE: simpletrack do not have album informations
    def expander_simple_track(self,
                              item: spotipy.model.track.SimpleTrack,
                              **kwargs
                              ) -> Generator[spotipy.model.track.Track, None, None]:

        opts = self.options.push(kwargs)
        yield from self.expander(self.spotify.track(item.id, market=self.market), **opts)

    def expander_artist(self,
                        item: spotipy.model.artist.Artist,
                        **kwargs
                        ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.__log.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False
        if self.is_uri_already_seen(item.uri):
            return

        # add as new source
        if opts.expand_artist_to_related_artists:
            self.add_artist_related_artists_as_source(item, **opts)
            did = True
        # add as new source
        if opts.expand_artist_to_recommendations:
            self.add_artist_recommendations_as_source(item, **opts)
            did = True
        # yield tracks
        if opts.expand_artist_to_albums:
            yield from self.expand_artist_to_albums(item, **opts)
            did = True
        elif opts.expand_artist_to_top_tracks:
            yield from self.expand_artist_to_top_tracks(item, **opts)
            did = True
        # nice hack
        if not did:
            self.__log.warning('did not do anything with: %s', item.uri)

    def expand_artist_to_albums(self,
                                artist: spotipy.model.artist.Artist,
                                **kwargs) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(artist.uri + '#albums'):
            return
        e = self.expander(self.randomizer(
                self.artist_albums_generator(artist.id),
                **opts), **opts)
        yield from e

    def expand_artist_to_top_tracks(self,
                                    artist: spotipy.model.artist.Artist,
                                    **kwargs) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(artist.uri + '#top-tracks'):
            return
        e = self.expander(self.randomizer(
                self.artist_top_tracks_generator(artist.id),
                **opts), **opts)
        yield from e

    def expander_album(self,
                       item: spotipy.model.album.Album,
                       **kwargs
                       ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.__log.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False
        if self.is_uri_already_seen(item.uri):
            return

        # add as new source
        if opts.expand_album_to_artists:
            self.add_album_artists_as_source(item, **opts)
            did = True

        if opts.expand_album_to_tracks:
            yield from self.expand_album_to_tracks(item, **opts)
            did = True

        if not did:
            self.__log.warning('did not do anything with: %s', item.uri)

    def expand_album_to_tracks(self,
                               album: spotipy.model.album.Album,
                               **kwargs) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(album.uri + '#tracks'):
            return
        opts.set(expand_track_to_album=False)
        e = self.expander(self.album_tracks_generator(album.id), **opts)
        yield from e

    def add_album_artists_as_source(self,
                                    album: spotipy.model.album.Album,
                                    **kwargs) -> None:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(album.uri + '#artists'):
            return
        for artist in album.artists:
            self.add_artist_as_source(artist, **opts)

    def expander_playlist(self,
                          item: spotipy.model.playlist.Playlist,
                          **kwargs
                          ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.__log.debug('%s:%s: %s', item.type, item.id, item.name)
        if self.is_uri_already_seen(item.uri):
            return
        elif opts.expand_playlist_to_tracks:
            yield from self.expand_playlist_to_tracks(item, **opts)
        else:
            self.__log.warning('did not do anything with: %s', item.uri)

    def expand_playlist_to_tracks(self,
                                  playlist: spotipy.model.playlist.Playlist,
                                  **kwargs) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.is_uri_already_seen(playlist.uri + '#tracks'):
            return
        e = self.expander(self.randomizer(
                self.playlist_all_tracks_generator(playlist.id),
                **opts), **opts)
        yield from e

    # TODO: add uri model class
    # NOTE: not used by expander
    def expand_uri(self,
                   item: str,
                   **kwargs) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        item_type, item_id = spotipy.convert.from_uri(item)
        self.__log.debug('%s: %s', item_type, item_id)
        if item_type == 'artist':
            yield from self.expander(self.spotify.artist(item_id), **opts)
        elif item_type == 'album':
            yield from self.expander(self.spotify.album(item_id, market=self.market), **opts)
        elif item_type == 'track':
            yield from self.expander(self.spotify.track(item_id, market=self.market), **opts)
        elif item_type == 'playlist':
            yield from self.expander(self.spotify.playlist(item_id, market=self.market), **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    def uris_to_items(self, uris: List) -> List:

        items = list()
        for uri in uris:
            uri_type, uri_id = spotipy.convert.from_uri(uri)
            self.__log.debug('%s: %s', uri_type, uri_id)
            if uri_type == 'artist':
                items.append(self.spotify.artist(uri_id))
            elif uri_type == 'album':
                items.append(self.spotify.album(uri_id, market=self.market))
            elif uri_type == 'track':
                items.append(self.spotify.track(uri_id, market=self.market))
            elif uri_type == 'playlist':
                items.append(self.spotify.playlist(uri_id, market=self.market))
            else:
                self.__log.warning('unsupported uri: %s (%s, %s)', uri, uri_type, uri_id)
        return items

# END
