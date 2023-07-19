#
#

from typing import List, Set, Generator, Union, Any, Dict, cast, Optional
from collections.abc import Iterable

import logging
import pprint
import types
import random
import operator
import functools

import enlighten
import more_itertools

from toukka.sopiva.spotify.model import (
    FullTrack, SimpleTrack, Track,
    FullAlbum, SimpleAlbum, Album,
    FullArtist, SimpleArtist, Artist,
    FullEpisode, SimpleEpisode, Episode,
    FullShow, SimpleShow, Show,
    FullPlaylist, SimplePlaylist, Playlist,
    PlaylistTrack,
    FullPlaylistTrack, LocalPlaylistTrack, FullPlaylistEpisode
)

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.genres import Genre

from toukka.sopiva.spotify_history.util import get_spotify_history

import toukka.sopiva.spotify_manager.genres

from .model import SpotifyUri, Label
from .playlist import PlaylistModifier
from .sources_queue import SourcesQueue
from .track_filter import TrackFilter
from .util import scramble_generator, take_random_items_generator, empty_generator
from .progress_bar import ProgressBars
from .seen import Seen
from .banner import UriBanDict
from .options import PlaylistGeneratorOptions
from .counter import ItemCounter

from .ignores import VARIOUS_ARTISTS, CLASSICAL_ARTISTS


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PlaylistGenerator(PlaylistGeneratorOptions):
    '''generates playlist'''

    def __init__(
            self,
            playlist_uri: str = None,
            **kwargs
            ) -> None:

        super().__init__(**kwargs)

        # TODO: move?
        self.logger = logger

        self.spotify = get_spotify(token_type='client')

        with self.spotify.user_as():
            self.user_country = self.spotify.current_user().country

        # disabling track relinking
        self.market = None
        # init empty
        self._uris_seen = Seen()
        # TODO: move to PlaylistModifier or remove?
        self.uris_to_playlist: List[str] = list()
        self.uriban = UriBanDict()

        self.playlist = PlaylistModifier(uri=playlist_uri, spotify=self.spotify)
        self.sources = SourcesQueue()
        self.track_filter = TrackFilter(
            spotify=self.spotify,
            user_country=self.user_country,
            played_count_min=self.options.played_count_min)
        self.spotify_history = get_spotify_history()
        self.counter = ItemCounter()

    def generate(self, **kwargs) -> None:
        options = self.options.push(kwargs)
        self.looper(**options)

    def looper(self, **kwargs) -> None:
        options = self.options.push(kwargs)

        # FIXME: move?
        progress_bars = ProgressBars(enabled=options.progress_bar)
        # NOTE: order means something
        progress_added = progress_bars.progress_bar_for_tracks(options.looper_target_count)
        progress_looper = progress_bars.progress_bar_for_loops(options.looper_max_tries)

        sources_generator = self.sources.generator()

        for counter, item in enumerate(sources_generator, start=1):

            # ...
            if counter % 10 == 0:
                self.logger.debug(
                    'items: %i/%i, sources: %iD %iQ',
                    len(self.uris_to_playlist),
                    counter,
                    self.sources.sources_used_count,
                    len(self.sources))
                self.logger.debug(self.counter.most_common())

            progress_looper.update()

            if self.track_filter.is_ok(item):
                # TODO: remove?
                self.uris_to_playlist.append(item.uri)
                # TODO: use this
                self.playlist.track_add(item.uri)
                self.logger.debug('%s:%s: added', item.type, item.id)
                progress_added.update()

            if len(self.uris_to_playlist) >= options.looper_target_count:
                self.logger.info('we have enough items (target count)')
                break

            # playlist can contains only ~10000 tracks
            # (actually 11000 and then 500 ISE)
            if not options.looper_force and len(self.uris_to_playlist) >= 10000:
                self.logger.info('we have enough items (playlist max)')
                break

            # safety
            if counter >= options.looper_max_tries:
                self.logger.info('we have tried too many items')
                break

            # add tracks to playlist every 100
            if options.use_partial_commits and len(self.playlist.tracks_queue) >= 100:
                self.commit(**options)

        progress_bars.stop()
        # if something not yet added
        self.commit(**options)
        self.logger.info(f'{len(self.uris_to_playlist)} items should be added to playlist')
        self.logger.debug(self.counter.most_common())

    def commit(self, **kwargs) -> None:
        options = self.options.push(kwargs)
        self.playlist.commit(dry_run=options.dry_run)

    def generate_from_uris(
            self,
            uris: List,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        # grr, tuples can't randomized with random.shuffle
        if isinstance(uris, tuple):
            uris = list(uris)

        if options.randomize_uris:
            self.logger.debug('shuffling uris')
            random.shuffle(uris)

        # TODO: move?
        uris_ = [SpotifyUri(uri) for uri in uris]

        yielder = self.yielder(uris_, expander=True, **options)
        self.sources.add(yielder)

        self.playlist.description = ', '.join(uris)
        self.generate(**options)

    def generate_from_genres(
            self,
            genres: List[Genre],
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if options.randomize_genres:
            self.logger.debug('shuffling genres')
            random.shuffle(genres)

        yielder = self.yielder(genres, expander=True, **options)
        self.sources.add(yielder)

        genre_names = [genre.name for genre in genres]
        self.playlist.description = ', '.join(genre_names)

        self.generate(**options)

    def generate_from_search(
            self,
            query_type: str,
            query: str,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        search = self.search_generator(query_type=query_type, query=query)
        yielder = self.yielder(search,
                               expander=True,
                               randomize=options.randomize_search)
        self.sources.add(yielder)
        self.playlist.description = f'search {query_type} "{query}"'
        self.generate(**options)

    def generate_from_recommendations(
            self,
            seed_artist_uris: List = None,
            seed_track_uris: List = None,
            seed_genres: List = None,
            seed_attributes: Dict = None,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        seed_artist_ids: List[str] = list()
        if seed_artist_uris is not None:
            for artist in self.uris_to_items(seed_artist_uris):
                seed_artist_ids.append(artist.id)
        seed_track_ids: List[str] = list()
        if seed_track_uris is not None:
            for track in self.uris_to_items(seed_track_uris):
                seed_track_ids.append(track.id)

        # TODO: move seed_attributes validation here?

        r = self.recommendations_generator(
            seed_artist_ids=seed_artist_ids,
            seed_track_ids=seed_track_ids,
            seed_genres=seed_genres,
            seed_attributes=seed_attributes)

        yielder = self.yielder(r,
                               expander=True,
                               randomize=options.randomize_recommendations,
                               **options)

        self.sources.add(yielder)
        self.playlist.description = ', '.join((
            f'source: recommendations',
            f'{seed_artist_uris}',
            f'{seed_track_uris}',
            f'{seed_genres}'))

        self.generate(**options)

    def generate_from_labels(
            self,
            labels: list[str],
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if options.randomize_labels:
            self.logger.debug('shuffling labels')
            random.shuffle(labels)

        # TODO: move?
        labels_ = [Label(label) for label in labels]

        yielder = self.yielder(labels_, expander=True, **options)
        self.sources.add(yielder)
        self.playlist.description = ', '.join(labels)
        self.generate(**options)

    # NOTE: returns False when uri is OK and True when uri is NOT ok
    # TODO: rename? swap returns?
    def check_uri(
            self,
            uri: str,
            **kwargs
            ) -> bool:

        options = self.options.push(kwargs)

        ignore = options.ignore

        if options.ignore_classical_artists:
            if uri in CLASSICAL_ARTISTS:
                self.logger.debug('%s: classical artist (skipping)', uri)
                return True

        if ignore:
            if uri in ignore:
                self.logger.debug('%s: ignored (skipping)', uri)
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

        options = self.options.push(kwargs)

        # NOTE: valid include_groups: 'album', 'single', 'appears_on', 'compilation'
        if include_groups is None:
            self.logger.warning('include_groups is None')

        paging = self.spotify.artist_albums(
            artist_id,
            include_groups=include_groups,
            limit=50,
            market=self.market)

        albums = self.spotify.all_items(paging)

        for album in albums:

            # speed up things
            if self.user_country not in album.available_markets:
                self.logger.debug('album:%s: not available in %s', album.id, self.user_country)
                continue

            yield album

    def artist_top_tracks_generator(
            self,
            artist_id: str
            ) -> Generator[FullTrack, None, None]:

        yield from self.spotify.artist_top_tracks(artist_id, market=self.user_country)

    def album_tracks_generator(
            self,
            album_id: str
            ) -> Generator[SimpleTrack, None, None]:

        yield from self.spotify.album_tracks_all_list_cached(album_id)

    def show_episodes_generator(
            self,
            show_id: str,
            **kwargs
            ) -> Generator[SimpleTrack, None, None]:

        options = self.options.push(kwargs)

        paging = self.spotify.show_episodes(
            show_id,
            market=self.market)
        episodes = self.spotify.all_items(paging)

        # FIXME: move?
        if options.sort_show_episodes_by_keys:
            self.logger.debug('adding sorting by %s, reverse: %s',
                              options.sort_show_episodes_by_keys,
                              options.sort_show_episodes_reverse)
            episodes = sorted(episodes,
                              key=operator.attrgetter(*options.sort_show_episodes_by_keys),
                              reverse=options.sort_show_episodes_reverse)

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

    def playlist_all_items_generator(
            self,
            playlist_id: str
            ) -> Generator[PlaylistTrack, None, None]:

        paging = self.spotify.playlist_items(
            playlist_id=playlist_id,
            market=self.market)

        for item in self.spotify.all_items(paging):
            yield item

    def randomizer(
            self,
            generator: Iterable,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        # TODO: remove, not useful logging
        self.logger.debug('randomizing: %s', type(generator))

        yield from scramble_generator(generator)

    def sorter(
            self,
            items: Iterable,
            keys=None, reverse=False, randomize=False,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if isinstance(items, types.GeneratorType):
            logger.debug('converting generator to list')
            items = list(items)

        if keys:
            logger.debug('sorting by %s, reverse: %s', keys, reverse)
            items.sort(key=operator.attrgetter(*keys), reverse=reverse)

        elif randomize:
            logger.debug('randomizing')
            random.shuffle(items)

        yield from items

    def yielder(
            self,
            generator: Iterable,
            expander=False,
            randomizer=False,
            sorter=False,
            sorter_keys=None,
            sorter_reverse=None,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        # TODO: use sorter instead
        if randomizer:
            generator = self.randomizer(generator, **options)

        if sorter and sorter_keys:
            generator = self.sorter(generator, sorter_keys, sorter_reverse)

        if expander:
            generator = self.expander(generator, **options)

        yield from generator

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

        options = self.options.push(kwargs)
        # self.logger.debug('%s', type(item))

        for count, i in enumerate(item, start=1):
            # self.logger.debug('%s: %i/?', type(i), count)
            yield from self.yielder(i, expander=True, **options)

    @expander.register
    def expander_list(
            self,
            item: list,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)
        self.logger.debug('%s: %s', type(item), len(item))

        for count, i in enumerate(item, start=1):
            self.logger.debug('%s: %i/%i', type(i), count, len(item))
            yield from self.yielder(i, expander=True, **options)

    @expander.register
    def expander_track(
            self,
            item: Track,
            **kwargs
            ) -> Generator[Track, None, None]:

        options = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False

        # TODO: move?
        track_artist_uris = [artist.uri for artist in item.artists]

        for track_artist_uri in track_artist_uris:

            if options.ignore_classical_artists:
                if track_artist_uri in CLASSICAL_ARTISTS:
                    self.logger.debug('%s:%s: classical artist track (skipping)', item.type, item.id)
                    return

            if options.ignore:
                if track_artist_uri in options.ignore:
                    self.logger.debug('%s: track artist ignored (skipping)', track_artist_uri)
                    return

        # add as new source
        if options.expand_track_to_artists:
            # self.logger.debug('%s:%s: to artists', item.type, item.id)
            self.add_track_artists_as_source(item, **options)
            did = True

        # add as new source
        if options.expand_track_to_recommendations:
            # self.logger.debug('%s:%s: to recommendations', item.type, item.id)
            self.add_track_recommendations_as_source(item, **options)
            did = True

        # yields tracks
        if options.expand_track_to_album:
            # self.logger.debug('%s:%s: to album', item.type, item.id)
            yield from self.expand_track_to_album(item, **options)
            did = True
            # NOTE: 2022-10-17 is this ok?
            return

        # and finally use track if not seen
        if not self.check_uri(item.uri):
            yield item
            self.counter.plus(item.type)
            did = True

        # nice hack
        if not did:
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_track_to_album(
            self,
            track: Track,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if self.check_uri(track.uri + '#album'):
            return

        # only FullTrack has album property
        if not isinstance(track, FullTrack):
            self.logger.debug('%s:%s: to FullTrack (slow)', track.type, track.id)
            track = self.spotify.track(track.id, market=None)

        # makes mypy happy
        track = cast(FullTrack, track)

        album = self.spotify.album_cached(track.album.id, market=self.market)
        yielder = self.yielder(album, expander=True, **options)
        yield from yielder

    def add_artist_as_source(
            self,
            artist: Artist,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if self.check_uri(artist.uri + '#source'):
            return

        artist = self.spotify.artist_cached(artist.id)
        yielder = self.yielder(artist, expander=True, **options)
        self.sources.add(yielder)

    def add_track_recommendations_as_source(
            self,
            track: Track,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if self.check_uri(track.uri + '#recommendations'):
            return

        recommendations = self.recommendations_generator(seed_track_ids=[track.id])
        yielder = self.yielder(recommendations, expander=True, **options)
        self.sources.add(yielder)

    def add_track_artists_as_source(
            self,
            track: Track,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)
        if self.check_uri(track.uri + '#artists'):
            return
        # set expand_track_to_artists option to False, so we dont hit again
        # options.set(expand_track_to_artists=False)
        for artist in track.artists:
            self.add_artist_as_source(artist, **options)

    def add_artist_related_artists_as_source(
            self,
            artist: Artist,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if self.check_uri(artist.uri + '#related'):
            return

        artists = self.related_artists_generator(artist.id)
        yielder = self.yielder(artists,
                               expander=True,
                               randomizer=options.randomize_artists,
                               sorter=True,
                               sorter_keys=options.sort_artists_by_keys,
                               sorter_reverse=options.sort_artists_reverse,
                               **options)

        self.sources.add(yielder)

    def add_artist_recommendations_as_source(
            self,
            artist: Artist,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if self.check_uri(artist.uri + '#recommendations'):
            return

        recommendations = self.recommendations_generator(seed_artist_ids=[artist.id])
        yielder = self.yielder(recommendations,
                               expander=True,
                               randomizer=options.randomize_recommendations,
                               **options)
        self.sources.add(yielder)

    # TODO: remove, not needed
    # NOTE: simpletrack do not have album informations
    def expander_simple_track(
            self,
            item: SimpleTrack,
            **kwargs
            ) -> Generator[Track, None, None]:

        options = self.options.push(kwargs)

        self.logger.debug('%s:%s: SimpleTrack to FullTrack', item.type, item.id)

        track = self.spotify.track(item.id, market=self.market)
        yielder = self.yielder(track, **options)
        yield from yielder

    @expander.register
    def expander_artist(
            self,
            item: Artist,
            **kwargs
            ) -> Generator[FullTrack, None, None]:

        options = self.options.push(kwargs)
        if self.check_uri(item.uri):
            return

        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        self.counter.plus(item.type)
        did = False

        # add as new source
        if options.expand_artist_to_related_artists:
            self.add_artist_related_artists_as_source(item, **options)
            did = True
        # add as new source
        if options.expand_artist_to_recommendations:
            self.add_artist_recommendations_as_source(item, **options)
            did = True
        # yield tracks
        if options.expand_artist_to_albums or options.expand_artist_to_random_album:
            yield from self.expand_artist_to_albums(item, **options)
            did = True
        elif options.expand_artist_to_top_tracks:
            yield from self.expand_artist_to_top_tracks(item, **options)
            did = True
        # nice hack
        if not did:
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_artist_to_albums(
            self,
            artist: Artist,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if self.check_uri(artist.uri + '#albums'):
            return

        albums = self.artist_albums_generator(
            artist.id,
            include_groups=options.include_album_groups)

        if options.expand_artist_to_random_album:
            albums = take_random_items_generator(albums)

        yielder = self.yielder(albums,
                               expander=True,
                               randomizer=options.randomize_albums,
                               sorter=True,
                               sorter_keys=options.sort_artist_albums_by_keys,
                               sorter_reverse=options.sort_artist_albums_reverse,
                               **options)
        yield from yielder

    def expand_artist_to_top_tracks(
            self,
            artist: Artist,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if self.check_uri(artist.uri + '#top-tracks'):
            return

        tracks = self.artist_top_tracks_generator(artist.id)
        yielder = self.yielder(tracks,
                               expander=True,
                               randomizer=options.randomize_tracks,
                               **options)
        yield from yielder

    @expander.register
    def expander_album(
            self,
            item: Album,
            **kwargs
            ) -> Generator[FullTrack, None, None]:

        options = self.options.push(kwargs)
        did = False

        if self.check_uri(item.uri):
            return

        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        self.counter.plus(item.type)

        # TODO: move?
        album_artist_uris = [artist.uri for artist in item.artists]

        for album_artist_uri in album_artist_uris:

            if options.ignore_various_artists:
                if album_artist_uri in VARIOUS_ARTISTS:
                    self.logger.debug('%s:%s: various artists album (skipping)', item.type, item.id)
                    return

            if options.ignore_classical_artists:
                if album_artist_uri in CLASSICAL_ARTISTS:
                    self.logger.debug('%s:%s: classical artist album (skipping)', item.type, item.id)
                    return

            if options.ignore:
                if album_artist_uri in options.ignore:
                    self.logger.debug('%s: album artist ignored (skipping)', album_artist_uri)
                    return

        # is played
        if options.ignore_played_albums:
            if self.is_album_played(item.id):
                self.logger.debug('%s:%s: album is already played (skipping)', item.type, item.id)
                return

        # TODO: rename option and crate album features only once...
        # is instrumental
        if options.ignore_non_instrumental_albums:
            if not self.spotify.album_features_df_cached(item.id).is_instrumental():
                self.logger.debug('%s:%s: album is not instrumental (skipping)', item.type, item.id)
                return

        # is energetic
        if options.only_energetic:
            if not self.spotify.album_features_df_cached(item.id).is_energetic():
                self.logger.debug('%s:%s: album is not energetic (skipping)', item.type, item.id)
                return

        # add as new source
        if options.expand_album_to_artists:
            self.add_album_artists_as_source(item, **options)
            did = True

        if options.expand_album_to_recommendations:
            self.add_album_tracks_to_recommendations_as_source(item, **options)
            did = True

        if options.expand_album_to_tracks:
            yield from self.expand_album_to_tracks(item, **options)
            did = True

        if not did:
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_album_to_tracks(
            self,
            album: Album,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if self.check_uri(album.uri + '#tracks'):
            return

        # NOTE: 20210620 - not really needed
        # NOTE: 20210620 - but without it, multiple track->fulltrack->album calls
        options.set(expand_track_to_album=False)

        tracks = self.album_tracks_generator(album.id)
        yielder = self.yielder(tracks, expander=True, **options)
        yield from yielder

    def add_album_tracks_to_recommendations_as_source(
            self,
            album: Album,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if self.check_uri(album.uri + '#recommendations'):
            return

        # TODO: slice to five
        tracks = self.album_tracks_generator(album.id)
        for track in tracks:
            self.add_track_recommendations_as_source(track, **options)

    def add_album_artists_as_source(
            self,
            album: Album,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if self.check_uri(album.uri + '#artists'):
            return

        for artist in album.artists:
            self.add_artist_as_source(artist, **options)

    @expander.register
    def expander_playlist(
            self,
            item: Playlist,
            **kwargs
            ) -> Generator[FullTrack, None, None]:

        options = self.options.push(kwargs)

        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        self.counter.plus(item.type)

        if self.check_uri(item.uri):
            return

        if options.expand_playlist_to_items:
            yield from self.expand_playlist_to_items(item, **options)
        else:
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_playlist_to_items(
            self,
            playlist: Playlist,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if self.check_uri(playlist.uri + '#tracks'):
            return

        playlist_tracks = self.playlist_all_items_generator(playlist.id)
        yielder = self.yielder(playlist_tracks,
                               expander=True,
                               randomizer=options.randomize_playlist_items,
                               **options)
        yield from yielder

    @expander.register
    def expand_playlistrack(
            self,
            item: PlaylistTrack,
            **kwargs
            ) -> Generator[Union[FullPlaylistTrack, LocalPlaylistTrack, FullPlaylistEpisode], None, None]:

        options = self.options.push(kwargs)
        self.counter.plus('playlist_track')
        # logger.debug('playlist track: %s, %s', item.added_at, item.added_by.uri)

        # TODO: use item type

        if item.track is None:
            self.logger.warning('playlist track is None (ignoring)')
            return

        if item.is_local:
            self.logger.warning('playlist track is local (ignoring)')
            return

        yielder = self.yielder(item.track, expander=True, **options)
        yield from yielder

    @expander.register
    def expander_uri(
            self,
            uri: SpotifyUri,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if self.check_uri(uri + '#uri'):
            return

        item = self.spotify.uri_to_item(uri)
        yielder = self.yielder(item, expander=True, **options)
        yield from yielder

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

        options = self.options.push(kwargs)
        if self.check_uri(f'genre:{item.name}'):
            return

        self.logger.debug('%s:%s', 'genre', item.name)
        self.counter.plus('genre')

        did = False
        # yield
        if options.expand_genre_to_playlists:
            yield from self.expand_genre_to_playlists(item, **options)
            did = True

        # add as new source
        if options.expand_genre_to_related_genres:
            self.expand_genre_to_related_genres(item, **options)
            did = True

        # add as new source
        if options.expand_genre_to_artists:
            self.expand_genre_to_artists(item, **options)
            did = True

        if not did:
            self.logger.warning('did not do anything with: genre:%s', item.name)

    def expand_genre_to_playlists(
            self,
            genre: Genre,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)

        if self.check_uri(f'genre:{genre.name}#playlists'):
            return

        if genre.playlists is None:
            self.logger.debug('genre:%s: no playlists, skipping', genre.name)
            return

        # select only wanted playlists
        playlist_uris: List[str] = []

        try:
            uris = [genre.playlists[k] for k in options.include_genre_playlists]
        except KeyError as e:
            raise Exception(f'unknown playlist name: {e}')

        playlist_uris = list(filter(None, uris))
        playlist_uris_ = [SpotifyUri(uri) for uri in playlist_uris]

        yielder = self.yielder(playlist_uris_, expander=True, **options)
        yield from yielder

    def expand_genre_to_artists(
            self,
            genre: Genre,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if self.check_uri(f'genre:{genre.name}#artists'):
            return

        # genre.name is unicode and artists.genres contains ascii
        genre_name = genre.name

        artists = self.spotify.artists_by_genre_cached(genre_name)

        yielder = self.yielder(artists,
                               expander=True,
                               randomizer=options.randomize_artists,
                               sorter=True,
                               sorter_keys=options.sort_artists_by_keys,
                               sorter_reverse=options.sort_artists_reverse,
                               **options)

        self.sources.add(yielder)

    def expand_genre_to_related_genres(
            self,
            genre: Genre,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

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

        yielder = self.yielder(related_genres, expander=True, **options)
        self.sources.add(yielder)

    @expander.register
    def expander_show(
            self,
            item: Show,
            **kwargs
            ) -> Generator[Episode, None, None]:

        options = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False

        if self.check_uri(item.uri):
            return

        if options.expand_show_to_episodes:
            yield from self.expand_show_to_episodes(item, **options)
            did = True

        if not did:
            self.logger.warning('did not do anything with: %s', item.uri)

    def expand_show_to_episodes(
            self,
            show: Show,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)
        if self.check_uri(show.uri + '#episodes'):
            return
        options.set(expand_track_to_album=False)
        episodes = self.show_episodes_generator(show.id, **options)
        yielder = self.yielder(episodes, expander=True, **options)
        yield from yielder

    @expander.register
    def expander_episode(
            self,
            item: Episode,
            **kwargs
            ) -> Generator[Episode, None, None]:

        options = self.options.push(kwargs)
        self.logger.debug('%s:%s: %s', item.type, item.id, item.name)
        did = False
        if not self.check_uri(item.uri):
            yield item
            did = True
        if not did:
            self.logger.warning('did not do anything with: %s', item.uri)

    @expander.register
    def expander_label(
            self,
            item: Label,
            **kwargs
            ) -> Generator[Any, None, None]:

        options = self.options.push(kwargs)
        if self.check_uri(f'label:{item}'):
            return

        self.logger.debug('%s:%s', 'label', item)
        self.counter.plus('label')

        did = False

        # add as new source
        if options.expand_label_to_albums:
            self.expand_label_to_albums(item, **options)
            did = True

        if not did:
            self.logger.warning('did not do anything with: label:%s', item)

        # NOTE: without this method is not generator
        yield from empty_generator()

    def expand_label_to_albums(
            self,
            label: Label,
            **kwargs
            ) -> None:

        options = self.options.push(kwargs)

        if self.check_uri(f'label:{label}#albums'):
            return

        albums = self.spotify.albums_by_label(label)

        yielder = self.yielder(albums,
                               expander=True,
                               randomizer=options.randomize_albums,
                               sorter=True,
                               sorter_keys=options.sort_label_albums_by_keys,
                               sorter_reverse=options.sort_label_albums_reverse,
                               **options)

        self.sources.add(yielder)

    # MOVE?
    def is_album_played(self, album_id):
        album_tracks = self.spotify.album_tracks_all_list_cached(album_id)
        track_uris = [track.uri for track in album_tracks]
        return self.spotify_history.is_tracks_played(track_uris)


# END
