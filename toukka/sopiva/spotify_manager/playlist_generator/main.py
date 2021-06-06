#
#

from typing import List, Set, Generator, Union, Any, Dict, cast, Optional

import logging
import pprint
import types
import random
import operator
import functools

import enlighten
import more_itertools
import unidecode

from toukka.sopiva.spotify.model import (
    FullTrack, SimpleTrack, Track,
    FullAlbum, SimpleAlbum, Album,
    FullArtist, SimpleArtist, Artist,
    FullPlaylist, SimplePlaylist, Playlist,
    ModelList,
    Show, Episode
)

from toukka.sopiva.spotify_manager.filters import (
    make_multi_filter, make_filter_by_artist_genre
)

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.uri import SpotifyUri
from toukka.sopiva.spotify_manager.genres import Genre

import toukka.sopiva.spotify_manager.genres

from .playlist import PlaylistModifier
from .sources_queue import SourcesQueue
from .track_filter import TrackFilter
from .util import scramble_generator, take_random_items_generator
from .progress_bar import ProgressBars
from .seen import Seen
from .banner import UriBanDict
from .options import PlaylistGeneratorOptions


class PlaylistGenerator(PlaylistGeneratorOptions):
    '''generates playlist'''

    def __init__(
            self,
            playlist_uri: str = None,
            **kwargs
            ) -> None:

        super().__init__(**kwargs)

        # TODO: move?
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug('initialized %s', self)
        self.logger.debug('options %s', self.options)

        self.spotify = get_spotify()
        self.user_country = self.spotify.current_user().country
        # disabling track relinking
        self.market = None

        # init empty
        self._uris_seen = Seen()
        # TODO: move to PlaylistModifier
        self.uris_to_playlist: List[str] = list()

        self.uriban = UriBanDict()

        self.playlist = PlaylistModifier(uri=playlist_uri, spotify=self.spotify)
        self.sources = SourcesQueue()
        self.track_filter = TrackFilter(
            spotify=self.spotify,
            user_country=self.user_country)


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
        track: Track

        for counter, track in enumerate(sources):

            self.logger.debug(
                'counter: %i, tracks: %i, sources: %i/%i',
                counter,
                len(self.uris_to_playlist),
                self.sources.sources_used_count,
                len(self.sources))

            progress_looper.update()

            # TODO: GRR
            if isinstance(track, Episode):
                self.uris_to_playlist.append(track.uri)
                self.logger.debug('episode:%s: added', track.id)
                continue

            # TODO: remove
            # actually we do not care as long track.id is usable
            if not isinstance(track, Track):
                raise Exception(f'wrong type received: {type(track)}')

            if self.track_filter.is_track_ok_to_add(track):
                self.uris_to_playlist.append(track.uri)
                self.logger.debug('track:%s: added', track.id)
                progress_tracks.update()

            if len(self.uris_to_playlist) >= opts.looper_target_count:
                self.logger.info('we have enough tracks to add (target count)')
                break

            # playlist can contains only ~10000 tracks
            # (actually 11000 and then 500 ISE)
            if len(self.uris_to_playlist) >= 10000:
                self.logger.info('we have enough tracks to add (playlist max)')
                break

            # safety
            if counter >= opts.looper_max_tries:
                self.logger.info('we have tried too many tracks')
                break

        progress_bars.stop()

        self.logger.info(f'{len(self.uris_to_playlist)} tracks to add')

    # TODO: split and move to Playlist
    def commit(self, **kwargs) -> None:
        opts = self.options.push(kwargs)

        if not opts.dry_run:
            if len(self.uris_to_playlist) > 0:
                self.playlist.clear()
                self.playlist.uris_add(self.uris_to_playlist)
                self.playlist.details_update()
            else:
                self.logger.info('try something else?')
        else:
            self.logger.info('dry_run is True, not committing')
        self.logger.info('done')

    def generate_from_uris(
            self,
            uris: List,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        self.logger.debug('method options: %s', opts)

        # grr, tuples can't randomized
        if isinstance(uris, tuple):
            self.logger.debug('uris is tuple, not list')
            uris = list(uris)

        if opts.randomize:
            self.logger.debug('shuffling uris')
            random.shuffle(uris)

        for uri in uris:
            self.sources.add(self.expander(SpotifyUri(uri), **opts))

        self.playlist.description = ', '.join(uris)
        self.generate(**opts)

    def generate_from_genres(
            self,
            genres: List[Genre],
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        self.logger.debug('method options: %s', opts)

        if opts.randomize:
            self.logger.debug('shuffling genres')
            random.shuffle(genres)

        genre_names: List[str] = []
        for genre in genres:
            self.sources.add(self.expander(genre, **opts))
            genre_names.append(genre.name)

        self.playlist.description = ', '.join(genre_names)
        self.generate(**opts)

    def generate_from_search(
            self,
            query_type: str,
            query: str,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)
        self.logger.debug('method options: %s', opts)

        s = self.search_generator(query_type=query_type, query=query)
        e = self.expander(self.randomizer(s, **opts), **opts)
        self.sources.add(e)
        self.playlist.description = f'search {query_type} "{query}"'
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
        self.logger.debug('method options: %s', opts)

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
            self.logger.debug('%s: banned (skipping)', uri)
            return True

        return self._uris_seen.see(uri)

    # generators

    def artist_albums_generator(
            self,
            artist_id: str,
            include_groups: Optional[List] = None,
            **kwargs
            ) -> Generator[FullAlbum, None, None]:

        opts = self.options.push(kwargs)

        # NOTE: valid include_groups: 'album', 'single', 'appears_on', 'compilation'
        if include_groups is None:
            self.logger.warning('include_groups is None')
        paging = self.spotify.artist_albums(
            artist_id,
            include_groups=include_groups,
            limit=50,
            market=self.market)

        albums = self.spotify.all_items(paging)

        # FIXME: move?
        if opts.sort_artist_albums_by_keys:
            self.logger.debug('adding sorting by %s, reverse: %s',
                             opts.sort_artist_albums_by_keys,
                             opts.sort_artist_albums_reverse)
            albums = sorted(albums,
                            key=operator.attrgetter(*opts.sort_artist_albums_by_keys),
                            reverse=opts.sort_artist_albums_reverse)

        for album in albums:
            # speed up things
            if self.user_country not in album.available_markets:
                self.logger.debug('album:%s: is not available %s', album.id, self.user_country)
                continue
            yield album

    def artist_top_tracks_generator(
            self,
            artist_id: str
            ) -> Generator[FullTrack, None, None]:

        yield from self.spotify.artist_top_tracks(
            artist_id,
            market=self.user_country)

    def album_tracks_generator(
            self,
            album_id: str
            ) -> Generator[SimpleTrack, None, None]:

        paging = self.spotify.album_tracks(
            album_id,
            market=self.market)
        yield from self.spotify.all_items(paging)

    def show_episodes_generator(
            self,
            show_id: str,
            **kwargs
            ) -> Generator[SimpleTrack, None, None]:

        opts = self.options.push(kwargs)

        paging = self.spotify.show_episodes(
            show_id,
            market=self.market)
        episodes = self.spotify.all_items(paging)

        # FIXME: move?
        if opts.sort_artist_albums_by_keys:
            self.logger.debug('adding sorting by %s, reverse: %s',
                             opts.sort_show_episodes_by_keys,
                             opts.sort_show_episodes_reverse)
            episodes = sorted(episodes,
                              key=operator.attrgetter(*opts.sort_show_episodes_by_keys),
                              reverse=opts.sort_show_episodes_reverse)

        yield from episodes

    def recommendations_generator(
            self,
            seed_artist_ids: List = None,
            seed_track_ids: List = None,
            seed_genres: List = None,
            seed_attributes: Dict = None
            ) -> Generator[FullTrack, None, None]:

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
            self.logger.debug(seed)
        yield from recommendations.tracks

    def related_artists_generator(
            self,
            artist_id: str
            ) -> Generator[FullArtist, None, None]:

        yield from self.spotify.artist_related_artists(artist_id)

    def search_generator(
            self,
            query_type: str,
            query: str
            ) -> Generator[
                    Union[FullTrack,
                          SimpleAlbum,
                          FullArtist,
                          SimplePlaylist],
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
            ) -> Generator[FullTrack, None, None]:

        paging = self.spotify.playlist_items(
            playlist_id=playlist_id,
            limit=100,
            market=self.market)

        for playlist_item in self.spotify.all_items(paging):
            if playlist_item.track is not None and not playlist_item.is_local:
                yield playlist_item.track

    # FIXME: generator -> iterable
    def randomizer(
            self,
            generator: Generator,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)

        if opts.randomize:
            self.logger.debug('randomizing: %s', type(generator))
            yield from scramble_generator(generator)
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

    @functools.singledispatchmethod
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
            self.logger.warning('did not do anything with: %s', item)

    # FIXME: is used?
    def expander_modellist(
            self,
            item: ModelList,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        self.logger.debug('%s: %s', type(item), len(item))

        if opts.expand_modellist_to_items:
            for item_ in item:
                yield from self.expander(item_, **opts)
        else:
            self.logger.warning('did not do anything with: %s', item)

    @expander.register
    def expander_track(
            self,
            item: Track,
            **kwargs
            ) -> Generator[Track, None, None]:

        opts = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
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
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_track_to_album(
            self,
            track: Track,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.check_uri(track.uri + '#album'):
            return
        # only FullTrack has album property
        if not isinstance(track, FullTrack):
            track = self.spotify.track(track.id, market=None)
        # makes mypy happy
        track = cast(FullTrack, track)
        album = self.spotify.album(track.album.id, market=self.market)
        # set expand_track_to_album option False, so we dont hit again
        # opts.set(expand_track_to_album=False)
        e = self.expander(album, **opts)
        yield from e

    def add_artist_as_source(
            self,
            artist: Artist,
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
            track: Track,
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
            track: Track,
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
            artist: Artist,
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
            artist: Artist,
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
            item: SimpleTrack,
            **kwargs
            ) -> Generator[Track, None, None]:

        opts = self.options.push(kwargs)
        yield from self.expander(self.spotify.track(item.id, market=self.market), **opts)

    @expander.register
    def expander_artist(
            self,
            item: Artist,
            **kwargs
            ) -> Generator[FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
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
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_artist_to_albums(
            self,
            artist: Artist,
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
            artist: Artist,
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
            item: Album,
            **kwargs
            ) -> Generator[FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False
        if self.check_uri(item.uri):
            return

        # TODO: move?
        if opts.exclude_various_artists_albums:
            various_artists_id = '0LyfQWJT6nXafLPZqxe9Of'
            artist_ids = [artist.id for artist in item.artists]
            if various_artists_id in artist_ids:
                self.logger.debug('%s:%s: various artists album, ignoring', item.type, item.id)
                return

        # add as new source
        if opts.expand_album_to_artists:
            self.add_album_artists_as_source(item, **opts)
            did = True

        if opts.expand_album_to_tracks:
            yield from self.expand_album_to_tracks(item, **opts)
            did = True

        if not did:
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_album_to_tracks(
            self,
            album: Album,
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
            album: Album,
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
            item: Playlist,
            **kwargs
            ) -> Generator[FullTrack, None, None]:

        opts = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        if self.check_uri(item.uri):
            return
        elif opts.expand_playlist_to_tracks:
            yield from self.expand_playlist_to_tracks(item, **opts)
        else:
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_playlist_to_tracks(
            self,
            playlist: Playlist,
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
            uri: SpotifyUri,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        uri_type, uri_id = self.spotify.convert.from_uri(uri)
        self.logger.debug('%s: %s: %s', uri, uri_type, uri_id)
        if self.check_uri(uri + '#uri'):
            return

        item_object = self.spotify.uri_to_item(uri)
        yield from self.expander(item_object, **opts)

    # TODO: remove
    def uris_to_items(self, uris: List) -> List:

        items = list()
        for uri in uris:
            uri_type, uri_id = self.spotify.convert.from_uri(uri)
            self.logger.debug('%s: %s', uri_type, uri_id)
            items.append(self.spotify.uri_to_item(uri))
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
        self.logger.debug('%s:%s', 'genre', item.name)
        did = False
        # yield
        if opts.expand_genre_to_playlists:
            yield from self.expand_genre_to_playlists(item, **opts)
            did = True

        # add as new source
        if opts.expand_genre_to_related_genres:
            self.expand_genre_to_related_genres(item, **opts)
            did = True

        # add as new source
        if opts.expand_genre_to_artists:
            self.expand_genre_to_artists(item, **opts)
            did = True

        if not did:
            self.logger.warning('did not do anything with: genre:%s', item.name)

    def expand_genre_to_playlists(
            self,
            genre: Genre,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)

        if self.check_uri(f'genre:{genre.name}#playlists'):
            return

        if genre.playlists is None:
            self.logger.debug('genre:%s: no playlists, skipping', genre.name)
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

    def expand_genre_to_artists(
            self,
            genre: Genre,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)

        if self.check_uri(f'genre:{genre.name}#artists'):
            return

        # genre.name is unicode and artists.genres contains ascii
        genre_name = unidecode.unidecode(genre.name)

        query = f'genre:"{genre_name}"'
        query_type = 'artist'

        search = self.search_generator(query_type=query_type, query=query)
        # search genre matches substrings, so filter
        search = filter(make_filter_by_artist_genre(genre_name), search)
        expander = self.expander(self.randomizer(search, **opts), **opts)
        self.sources.add(expander)

    def expand_genre_to_related_genres(
            self,
            genre: Genre,
            **kwargs
            ) -> None:

        opts = self.options.push(kwargs)

        if self.check_uri(f'genre:{genre.name}#related'):
            return

        if genre.related is None:
            self.logger.debug('genre:%s: no related genres, skipping', genre.name)
            return

        genres = toukka.sopiva.spotify_manager.genres.genres()
        related_genres = list()
        for related_genre_name in genre.related:
            related_genre = genres.get(related_genre_name)
            if related_genre is None:
                self.logger.debug('genre:%s: not found, skipping', related_genre_name)
                continue

            related_genres.append(related_genre)

        # NOTE: convert list to _generator_, cos im stupid
        related_genres = (i for i in related_genres)
        expander = self.expander(related_genres, **opts)
        self.sources.add(expander)

    @expander.register
    def expander_show(
            self,
            item: Show,
            **kwargs
            ) -> Generator[Episode, None, None]:

        opts = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False

        if self.check_uri(item.uri):
            return

        if opts.expand_show_to_episodes:
            yield from self.expand_show_to_episodes(item, **opts)
            did = True

        if not did:
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_show_to_episodes(
            self,
            show: Show,
            **kwargs
            ) -> Generator[Any, None, None]:

        opts = self.options.push(kwargs)
        if self.check_uri(show.uri + '#episodes'):
            return
        opts.set(expand_track_to_album=False)
        episodes = self.show_episodes_generator(show.id, **opts)
        e = self.expander(episodes, **opts)
        yield from e

    @expander.register
    def expander_episode(
            self,
            item: Episode,
            **kwargs
            ) -> Generator[Episode, None, None]:

        opts = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False
        if not self.check_uri(item.uri):
            yield item
            did = True
        if not did:
            self.logger.warning('did not do anything with: %s', item.uri)


# END
