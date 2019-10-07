#
#

import logging
import pprint

import spotipy.convert
import toukka.config

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history
from toukka.sopiva.spotify.printer import first as printer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _get_playlist_uri_from_config():
    return toukka.config.lazy_config['spotify_manager']['playlist_generator']['playlist_uri'].get()


class PlaylistGenerator:
    def __init__(self, playlist_uri=None):
        self.spotify = get_spotify()
        self.spotify_history = get_spotify_history()

        if playlist_uri is None:
            playlist_uri = _get_playlist_uri_from_config()
        playlist_uri_type, playlist_uri_id = spotipy.convert.from_uri(playlist_uri)
        self.playlist = self.spotify.playlist(playlist_uri_id)
        self.playlist_snapshot_id = self.playlist.snapshot_id

        self._isrc_seen = set()

        # FIXME:
        filter_played = True
        filter_duplicate_isrc = True

    def looper(self, tracks):
        track_ids_to_playlist = list()

        for track in tracks:
            printer.print_track(track)

            if self.is_track_ok_to_add(track):
                track_ids_to_playlist.append(track.id)

            if len(track_ids_to_playlist) >= 200:
                print('we have enough tracks to add')
                break

        print(f'{len(track_ids_to_playlist)} tracks to add')

        self.playlist_clear()
        self.playlist_tracks_add(track_ids_to_playlist)

        print('done')

    def generate_playlist_from_artist_id(self, artist_id):
        self.looper(self.iterate_artist_all_tracks(artist_id))

    def generate_playlist_from_recommendations(self,
                                               seed_artist_ids: list = None,
                                               seed_track_ids: list = None,
                                               seed_genres: list = None):

        self.looper(self.iterate_recommendations(seed_artist_ids=seed_artist_ids,
                                                 seed_track_ids=seed_track_ids,
                                                 seed_genres=seed_genres))

    def is_track_ok_to_add(self, track):
        if self.is_track_isrc_already_added(track):
            print(f'{track.id}: isrc already added')
            return False
        elif self.is_track_already_played(track):
            print(f'{track.id}: already played')
            return False
        elif not self.is_track_playeable(track):
            print(f'{track.id}: not playeable')
            return False
        else:
            return True

    def is_track_already_played(self, track):
        if self.spotify_history.count_by_track_id(track.uri) > 0:
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

    # playlist modify methods

    def playlist_change_details(self, **kwargs):
        self.spotify.playlist_change_details(self.playlist.id, **kwargs)

    def playlist_clear(self):
        self.spotify.playlist_tracks_replace(self.playlist.id, [])

    def playlist_reload(self):
        self.playlist = self.spotify.playlist(self.playlist.id)

    def playlist_tracks_add(self, track_ids):
        chunks = self.list_to_chunks(track_ids, 100)
        for chunk in chunks:
            self.playlist_snapshot_id = self.spotify.playlist_tracks_add(self.playlist.id, chunk)

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

        albums = self.spotify.artist_albums(
            artist_id,
            include_groups=include_album_groups,
            market='FI')

        for album in self.spotify.iterate_items_from_paging(albums):
            print(f'{album.name}')

            # FIXME: move?
            if any(bad in album.name.lower() for bad in bad_word_in_album_names):
                print('bad album name, skipping')
                continue

            album_tracks = self.spotify.iterate_items_from_paging(
                self.spotify.album_tracks(album.id, market=None, limit=50))

            for simple_track in album_tracks:
                track = self.spotify.track(simple_track.id)
                yield track

    def iterate_recommendations(self,
                                seed_artist_ids: list = None,
                                seed_track_ids: list = None,
                                seed_genres: list = None):

        recommendations = self.spotify.recommendations(
                                                    artist_ids=seed_artist_ids,
                                                    track_ids=seed_track_ids,
                                                    genres=seed_genres,
                                                    limit=100)

        for seed in recommendations.seeds:
            seed.pprint()

        for track in recommendations.tracks:
            yield track


# END
