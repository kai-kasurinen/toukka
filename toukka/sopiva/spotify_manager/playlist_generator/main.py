#
#

import logging
import pprint
import itertools

import spotipy.convert
import spotipy.model.track

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

        # NOTE: BUG: with market='from_token' fails on unplayeble track -> TypeError
        self._market = None
        self._market_country_code = 'FI'

        # init empty
        self._isrc_seen = set()
        self._sources = list()

        # get playlist
        if playlist_uri is None:
            playlist_uri = _get_playlist_uri_from_config()
        playlist_uri_type, playlist_uri_id = spotipy.convert.from_uri(playlist_uri)
        self.playlist = self.spotify.playlist(playlist_uri_id, market=self._market)
        self.playlist_snapshot_id = self.playlist.snapshot_id

        # defaults
        self.playlist_name = '< g e n e r a t e d >'
        self.playlist_description = None

    def add_source(self, source):
        self._sources.append(source)

    def generate(self):
        # FIXME: remove argument
        self.looper(itertools.chain.from_iterable(self._sources))
        # FIXME: continue

    def looper(self, tracks):
        track_ids_to_playlist = list()

        for counter, track in enumerate(tracks):
            assert isinstance(track, spotipy.model.track.FullTrack)

            if track.id in track_ids_to_playlist:
                logger.debug(f'{track.id}: already added')

            if self.is_track_ok_to_add(track):
                printer.print_track(track)
                track_ids_to_playlist.append(track.id)

            if len(track_ids_to_playlist) >= 1000:
                print('we have enough tracks to add')
                break

            # safety
            if counter > 10000:
                print('we have tried too many tracks, breaking loop')
                break

        print(f'{len(track_ids_to_playlist)} tracks to add')

        if len(track_ids_to_playlist) > 0:
            self.playlist_clear()
            self.playlist_tracks_add(track_ids_to_playlist)
            self.playlist_details_update()
        else:
            print('try something else?')

        print('done')

    def generate_playlist_from_artist_id(self, artist_id):
        '''generate playlist from artist'''

        def update_description():
            artist = self.spotify.artist(artist_id)
            self.playlist_description = f'source: {artist.name} ({artist.uri})'

        update_description()
        source = self.iterate_artist_all_tracks(artist_id)
        self.add_source(source)
        self.generate()

    def generate_playlist_from_related_artists(self, artist_id):
        '''generate playlist from artist related artists'''

        def update_description():
            artist = self.spotify.artist(artist_id)
            self.playlist_description = f'source: {artist.name} ({artist.uri}) related artists'

        update_description()
        source = self.iterate_related_artists_all_tracks(artist_id)
        self.add_source(source)
        self.generate()

    def generate_playlist_from_playlist_id(self, playlist_id,
                                           expand_albums: bool = False,
                                           expand_artists: bool = False):
        '''generate playlist from other playlist'''

        def update_description():
            playlist = self.spotify.playlist(playlist_id=playlist_id, market=None)
            self.playlist_description = f'source: {playlist.name} ({playlist.uri})'

        update_description()
        source = self.iterate_playlist_all_tracks(playlist_id,
                                                  expand_albums=expand_albums,
                                                  expand_artists=expand_artists)
        self.add_source(source)
        self.generate()

    def generate_playlist_from_recommendations(self,
                                               seed_artist_ids: list = None,
                                               seed_track_ids: list = None,
                                               seed_genres: list = None,
                                               call_times: int = 1,
                                               expand_albums: bool = False,
                                               expand_artists: bool = False,
                                               **attributes):
        '''generate playlist from recommendations'''

        def update_description():
            self.playlist_description = f'source: recommendations'

        update_description()
        source = self.iterate_recommendations(seed_artist_ids=seed_artist_ids,
                                              seed_track_ids=seed_track_ids,
                                              seed_genres=seed_genres,
                                              call_times=call_times,
                                              expand_albums=expand_albums,
                                              expand_artists=expand_artists,
                                              **attributes)
        self.add_source(source)
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
    def list_to_chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    # track iterators

    def iterate_artist_all_tracks(self, artist_id: str):
        '''iterate artist all tracks'''
        # FIXME: move
        # NOTE: 'album', 'single', 'appears_on', 'compilation'
        include_album_groups = ['album', 'sinlge', 'compilation']
        bad_word_in_album_names = ['christmas']

        albums_paging = self.spotify.artist_albums(
            artist_id,
            include_groups=include_album_groups,
            market=self._market)

        for album in self.spotify.iterate_items_from_paging(albums_paging):
            logger.debug(album.name)

            # FIXME: move?
            if any(bad in album.name.lower() for bad in bad_word_in_album_names):
                logger.debug('bad album name, skipping')
                continue
            for track in self.iterate_album_tracks(album.id):
                yield track

    def iterate_album_tracks(self, album_id):
        album_tracks_paging = self.spotify.album_tracks(album_id,
                                                        market=self._market,
                                                        limit=50)
        album_tracks = self.spotify.iterate_items_from_paging(album_tracks_paging)

        for simple_track in album_tracks:
            track = self.spotify.track(simple_track.id, market=self._market)
            yield track

    def iterate_recommendations(self,
                                seed_artist_ids: list = None,
                                seed_track_ids: list = None,
                                seed_genres: list = None,
                                call_times: int = 1,
                                expand_albums: bool = False,
                                expand_artists: bool = False,
                                **attributes):

        # grr
        logger.debug(locals())
        # FIXME: hack
        for n in range(call_times):
            # BUG: attributes not used on spotipy
            recommendations = self.spotify.recommendations(
                                                    artist_ids=seed_artist_ids,
                                                    track_ids=seed_track_ids,
                                                    genres=seed_genres,
                                                    market=self._market,
                                                    limit=100,
                                                    **attributes)

            for seed in recommendations.seeds:
                logger.debug(seed)

            for track in recommendations.tracks:
                yield from self.track_expand(track,
                                             expand_album=expand_albums,
                                             expand_artist=expand_artists)

    def iterate_related_artists_all_tracks(self, artist_id):
        for artist in self.spotify.artist_related_artists(artist_id):
            yield from self.iterate_artist_all_tracks(artist.id)

    def iterate_search_tracks(self, query: str):
        '''search tracks'''
        search = self.spotify.search(query=query,
                                     limit=50,
                                     market=self._market)
        # FIXME: continue when BUG in next() fixed

    def iterate_playlist_all_tracks(self,
                                    playlist_id: str,
                                    expand_albums: bool = False,
                                    expand_artists: bool = False):
        logger.debug(locals())
        playlist = self.spotify.playlist(playlist_id=playlist_id, market=None)
        playlist_tracks = self.spotify.iterate_items_from_paging(playlist.tracks)
        for playlist_track in playlist_tracks:
            track = playlist_track.track
            yield from self.track_expand(track, expand_album=expand_albums, expand_artist=expand_artists)

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


# END
