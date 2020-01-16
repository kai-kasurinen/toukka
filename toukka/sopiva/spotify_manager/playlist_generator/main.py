#
#

from typing import List, Set, Generator, Union, Any, Dict, cast, Optional

import logging
import pprint
import types
import random
import operator

# import autologging
import enlighten
import more_itertools

from options import Options
# TODO: remove after upgraded to python3.8
from singledispatchmethod import singledispatchmethod

import spotipy.convert
import spotipy.serialise
import spotipy.model.track
import spotipy.model.artist
import spotipy.model.playlist
import spotipy.model.album

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.uri import SpotifyUri
from toukka.sopiva.spotify_manager.genres import Genre

import toukka.sopiva.spotify_manager.genres

from .playlist import Playlist
from .sources_queue import SourcesQueue
from .track_filter import TrackFilter
from .util import scramble_generator, take_random_items_generator
from .progress_bar import ProgressBars
from .seen import Seen
from .banner import UriBanDict


# @autologging.traced
# @autologging.logged
class PlaylistGenerator:
    '''generates playlist'''

    def __init__(
            self,
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
            expand_artist_to_random_album=False,
            expand_artist_to_top_tracks=False,
            expand_artist_to_related_artists=False,
            expand_artist_to_recommendations=False,
            expand_album_to_tracks=False,
            expand_album_to_artists=False,
            expand_playlist_to_tracks=False,
            expand_generator_to_items=True,
            expand_genre_to_playlists=False,
            expand_genre_to_related_genres=False,
            exclude_various_artists_albums=False,
            exclude_uris=False,
            include_album_groups=['album',
                                  'single',
                                  'compilation'],
            include_genre_playlists=['intro',
                                     'sound',
                                     'female',
                                     'year_2018',
                                     'year_2019',
                                     'pulse',
                                     'edge'],
            sort_artist_albums_by_keys=None,
            sort_artist_albums_reverse=False
        )

        self.options = options.push(kwargs)

        self.spotify = get_spotify()
        self.user_country = self.spotify.current_user().country
        # disabling track relinking
        self.market = None

        # init empty
        self._uris_seen = Seen()
        self.track_ids_to_playlist: List[str] = list()

        self.uriban = UriBanDict()

        self.playlist = Playlist(uri=playlist_uri, spotify=self.spotify)
        self.sources = SourcesQueue()
        self.track_filter = TrackFilter(
            spotify=self.spotify,
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

    def generate_from_uris(
            self,
            uris: List,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        self.__log.debug('method options: %s', opts)

        if opts.randomize:
            self.__log.debug('shuffling uris')
            random.shuffle(uris)
        for uri in uris:
            self.sources.add(self.expander(SpotifyUri(uri), **opts))
        self.playlist.description = f'source: {", ".join(uris)}'
        self.generate(**opts)

    def generate_from_genres(
            self,
            genres: List[Genre],
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        self.__log.debug('method options: %s', opts)
        genre_names: List[str] = []
        for genre in genres:
            self.sources.add(self.expander(genre, **opts))
            genre_names.append(genre.name)
        self.playlist.description = f'source: {", ".join(genre_names)}'
        self.generate(**opts)

    def generate_from_search(
            self,
            query_type: str,
            query: str,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        self.__log.debug('method options: %s', opts)

        s = self.search_generator(query_type=query_type, query=query)
        e = self.expander(self.randomizer(s, **opts), **opts)
        self.sources.add(e)
        self.playlist.description = f'source: search {query_type} "{query}"'
        self.generate(**opts)

    def generate_from_recommendations(
            self,
            seed_artist_uris: List = None,
            seed_track_uris: List = None,
            seed_genres: List = None,
            seed_attributes: Dict = None,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        self.__log.debug('method options: %s', opts)

        seed_artist_ids: List[str] = list()
        if seed_artist_uris is not None:
            for artist in self.uris_to_items(seed_artist_uris):
                seed_artist_ids.append(artist.id)
        seed_track_ids: List[str] = list()
        if seed_track_uris is not None:
            for track in self.uris_to_items(seed_track_uris):
                seed_track_ids.append(track.id)

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

    # NOTE: returns False when uri is OK and True when uri is NOT ok
    # TODO: rename? swap returns?
    def check_uri(
            self,
            uri: str,
            **kwargs
            ) -> bool:

        opts = self.options.push(kwargs)

        exclude_uris = opts.exclude_uris

        if exclude_uris:
            if uri in exclude_uris:
                return True

        if uri in self.uriban:
            self.__log.debug('%s: banned (skipping)', uri)

        return self._uris_seen.see(uri)

    # generators

    def artist_albums_generator(
            self,
            artist_id: str,
            include_groups: Optional[List] = None,
            **kwargs
            ) -> Generator[spotipy.model.album.full.FullAlbum, None, None]:

        opts = self.options.push(kwargs)

        # NOTE: valid include_groups: 'album', 'single', 'appears_on', 'compilation'
        if include_groups is None:
            self.__log.warning('include_groups is None')
        paging = self.spotify.artist_albums(
            artist_id,
            include_groups=include_groups,
            limit=50,
            market=self.market)

        albums = self.spotify.all_items(paging)

        # FIXME: move?
        if opts.sort_artist_albums_by_keys:
            self.__log.debug('adding sorting by %s, reverse: %s',
                             opts.sort_artist_albums_by_keys,
                             opts.sort_artist_albums_reverse)
            albums = sorted(albums,
                            key=operator.attrgetter(*opts.sort_artist_albums_by_keys),
                            reverse=opts.sort_artist_albums_reverse)

        for album in albums:
            # speed up things
            if self.user_country not in album.available_markets:
                self.__log.debug('album:%s: is not available %s', album.id, self.user_country)
                continue
            yield album

    def artist_top_tracks_generator(
            self,
            artist_id: str
            ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        yield from self.spotify.artist_top_tracks(
            artist_id,
            market=self.user_country)

    def album_tracks_generator(
            self,
            album_id: str
            ) -> Generator[spotipy.model.track.SimpleTrack, None, None]:

        paging = self.spotify.album_tracks(
            album_id,
            market=self.market,
            limit=50)
        yield from self.spotify.all_items(paging)

    def recommendations_generator(
            self,
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

    def related_artists_generator(
            self,
            artist_id: str
            ) -> Generator[spotipy.model.artist.FullArtist, None, None]:

        yield from self.spotify.artist_related_artists(artist_id)

    def search_generator(
            self,
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
        for item in self.spotify.all_items(paging):
            # NOTE: item can me track, album, artist, playlist ...
            yield item

    def playlist_all_tracks_generator(
            self,
            playlist_id: str
            ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        paging = self.spotify.playlist_tracks(playlist_id=playlist_id,
                                              limit=100,
                                              market=self.market)

        for playlist_track in self.spotify.all_items(paging):
            if playlist_track.track is not None and not playlist_track.is_local:
                yield playlist_track.track

    # FIXME: generator -> iterable
    def randomizer(
            self,
            generator: Generator,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)

        if opts.randomize:
            self.__log.debug('randomizing: %s', type(generator))
            yield from scramble_generator(generator, 100)
        else:
            yield from generator

    # TODO: rename? use?
    def expand_and_randomize(
            self,
            item,
            **kwargs
            ):
        opts = self.options.push(kwargs)
        return self.expander(self.randomizer(item, **opts), **opts)

    @singledispatchmethod
    def expander(
            self,
            item,
            **kwargs
            ):
        raise NotImplementedError('not yet supported expander type: %s' % type(item))

    @expander.register
    def expander_generator(
            self,
            item: types.GeneratorType,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if opts.expand_generator_to_items:
            for item_ in item:
                yield from self.expander(item_, **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    # FIXME: is used?
    def expander_modellist(
            self,
            item: spotipy.serialise.ModelList,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        self.__log.debug('%s: %s', type(item), len(item))

        if opts.expand_modellist_to_items:
            for item_ in item:
                yield from self.expander(item_, **opts)
        else:
            self.__log.warning('did not do anything with: %s', item)

    @expander.register
    def expander_track(
            self,
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
        if not self.check_uri(item.uri):
            yield item
            did = True
        # nice hack
        if not did:
            self.__log.warning('did not do anything with: %s', item.uri)

    def expand_track_to_album(
            self,
            track: spotipy.model.track.Track,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.check_uri(track.uri + '#album'):
            return
        # only FullTrack has album property
        if not isinstance(track, spotipy.model.track.FullTrack):
            track = self.spotify.track(track.id, market=None)
        # makes mypy happy
        track = cast(spotipy.model.track.FullTrack, track)
        album = self.spotify.album(track.album.id, market=self.market)
        # set expand_track_to_album option False, so we dont hit again
        # opts.set(expand_track_to_album=False)
        e = self.expander(album, **opts)
        yield from e

    def add_artist_as_source(
            self,
            artist: spotipy.model.artist.Artist,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        if self.check_uri(artist.uri + '#source'):
            return
        artist = self.spotify.artist(artist.id)
        e = self.expander(artist, **opts)
        self.sources.add(e)

    def add_track_recommendations_as_source(
            self,
            track: spotipy.model.track.Track,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        if self.check_uri(track.uri + '#recommendations'):
            return
        recommendations = self.recommendations_generator(seed_track_ids=[track.id])
        e = self.expander(self.randomizer(recommendations, **opts), **opts)
        self.sources.add(e)

    def add_track_artists_as_source(
            self,
            track: spotipy.model.track.Track,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        if self.check_uri(track.uri + '#artists'):
            return
        # set expand_track_to_artists option to False, so we dont hit again
        # opts.set(expand_track_to_artists=False)
        for artist in track.artists:
            self.add_artist_as_source(artist, **opts)

    def add_artist_related_artists_as_source(
            self,
            artist: spotipy.model.artist.Artist,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        if self.check_uri(artist.uri + '#related'):
            return
        artists = self.related_artists_generator(artist.id)
        e = self.expander(self.randomizer(artists, **opts), **opts)
        self.sources.add(e)

    def add_artist_recommendations_as_source(
            self,
            artist: spotipy.model.artist.Artist,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        if self.check_uri(artist.uri + '#recommendations'):
            return
        recommendations = self.recommendations_generator(seed_artist_ids=[artist.id])
        e = self.expander(self.randomizer(recommendations, **opts), **opts)
        self.sources.add(e)

    # TODO: remove, not needed
    # NOTE: simpletrack do not have album informations
    def expander_simple_track(
            self,
            item: spotipy.model.track.SimpleTrack,
            **kwargs
            ) -> Generator[spotipy.model.track.Track, None, None]:

        opts = self.options.push(kwargs)
        yield from self.expander(self.spotify.track(item.id, market=self.market), **opts)

    @expander.register
    def expander_artist(
            self,
            item: spotipy.model.artist.Artist,
            **kwargs
            ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.__log.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False
        if self.check_uri(item.uri):
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
        if opts.expand_artist_to_albums or opts.expand_artist_to_random_album:
            yield from self.expand_artist_to_albums(item, **opts)
            did = True
        elif opts.expand_artist_to_top_tracks:
            yield from self.expand_artist_to_top_tracks(item, **opts)
            did = True
        # nice hack
        if not did:
            self.__log.warning('did not do anything with: %s', item.uri)

    def expand_artist_to_albums(
            self,
            artist: spotipy.model.artist.Artist,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.check_uri(artist.uri + '#albums'):
            return

        albums = self.artist_albums_generator(
            artist.id,
            include_groups=opts.include_album_groups)

        if opts.expand_artist_to_random_album:
            albums = take_random_items_generator(albums)

        e = self.expander(self.randomizer(albums, **opts), **opts)
        yield from e

    def expand_artist_to_top_tracks(
            self,
            artist: spotipy.model.artist.Artist,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.check_uri(artist.uri + '#top-tracks'):
            return

        tracks = self.artist_top_tracks_generator(artist.id)
        e = self.expander(self.randomizer(tracks, **opts), **opts)
        yield from e

    @expander.register
    def expander_album(
            self,
            item: spotipy.model.album.Album,
            **kwargs
            ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.__log.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False
        if self.check_uri(item.uri):
            return

        # TODO: move?
        if opts.exclude_various_artists_albums:
            various_artists_id = '0LyfQWJT6nXafLPZqxe9Of'
            artist_ids = [artist.id for artist in item.artists]
            if various_artists_id in artist_ids:
                self.__log.debug('%s:%s: various artists album, ignoring', item.type, item.id)
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

    def expand_album_to_tracks(
            self,
            album: spotipy.model.album.Album,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.check_uri(album.uri + '#tracks'):
            return
        opts.set(expand_track_to_album=False)
        tracks = self.album_tracks_generator(album.id)
        e = self.expander(tracks, **opts)
        yield from e

    def add_album_artists_as_source(
            self,
            album: spotipy.model.album.Album,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        if self.check_uri(album.uri + '#artists'):
            return
        for artist in album.artists:
            self.add_artist_as_source(artist, **opts)

    @expander.register
    def expander_playlist(
            self,
            item: spotipy.model.playlist.Playlist,
            **kwargs
            ) -> Generator[spotipy.model.track.FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.__log.debug('%s:%s: %s', item.type, item.id, item.name)
        if self.check_uri(item.uri):
            return
        elif opts.expand_playlist_to_tracks:
            yield from self.expand_playlist_to_tracks(item, **opts)
        else:
            self.__log.warning('did not do anything with: %s', item.uri)

    def expand_playlist_to_tracks(
            self,
            playlist: spotipy.model.playlist.Playlist,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.check_uri(playlist.uri + '#tracks'):
            return
        tracks = self.playlist_all_tracks_generator(playlist.id)
        expander = self.expander(self.randomizer(tracks, **opts), **opts)
        yield from expander

    @expander.register
    def expander_uri(
            self,
            item: SpotifyUri,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        item_type, item_id = spotipy.convert.from_uri(item)
        self.__log.debug('%s: %s: %s', item, item_type, item_id)
        if self.check_uri(item + '#uri'):
            return
        if item_type == 'artist':
            item_object = self.spotify.artist(item_id)
        elif item_type == 'album':
            item_object = self.spotify.album(item_id, market=self.market)
        elif item_type == 'track':
            item_object = self.spotify.track(item_id, market=self.market)
        elif item_type == 'playlist':
            item_object = self.spotify.playlist(item_id, market=self.market)
        else:
            self.__log.warning('unsupported uri: %s', item)
            return
        yield from self.expander(item_object, **opts)

    # TODO: remove
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

    @expander.register
    def expander_genre(
            self,
            item: Genre,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.check_uri(f'genre:{item.name}'):
            return
        self.__log.debug('%s:%s', 'genre', item.name)
        did = False
        # yield
        if opts.expand_genre_to_playlists:
            yield from self.expand_genre_to_playlists(item, **opts)
            did = True

        # add as new source
        if opts.expand_genre_to_related_genres:
            self.expand_genre_to_related_genres(item, **opts)
            did = True

        if not did:
            self.__log.warning('did not do anything with: genre:%s', item.name)

    def expand_genre_to_playlists(
            self,
            genre: Genre,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)

        if self.check_uri(f'genre:{genre.name}#playlists'):
            return

        if genre.playlists is None:
            self.__log.debug('genre:%s: no playlists, skipping', genre.name)
            return

        # select only wanted playlists
        playlist_uris: List[str] = []
        try:
            uris = [genre.playlists[k] for k in opts.include_genre_playlists]
        except KeyError as e:
            raise Exception(f'unknown playlist name: {e}')
        playlist_uris = list(filter(None, uris))

        for playlist_uri in playlist_uris:
            yield from self.expander(SpotifyUri(playlist_uri), **opts)

    def expand_genre_to_related_genres(
            self,
            genre: Genre,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)

        if self.check_uri(f'genre:{genre.name}#related'):
            return

        if genre.related is None:
            self.__log.debug('genre:%s: no related genres, skipping', genre.name)
            return

        genres = toukka.sopiva.spotify_manager.genres.genres()
        for related_genre_name in genre.related:
            related_genre = genres.get(related_genre_name)
            if related_genre is None:
                self.__log.debug('genre:%s: not found, skipping', related_genre_name)
                continue

            expander = self.expander(related_genre, **opts)
            self.sources.add(expander)


# END
