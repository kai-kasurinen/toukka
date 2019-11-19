#

from typing import List, Set, Generator, Union

import logging
import spotipy

from spotipy.model.track import FullTrack, Track
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history
# TODO: rewrite


class TrackFilter:

    def __init__(self,
                 spotify: spotipy.Spotify = None,
                 track_ids_to_playlist: list = None,
                 user_country: str = None
                 ) -> None:
        self.spotify = spotify or get_spotify()
        self.spotify_history = get_spotify_history()
        self.user_country = user_country
        # FIXME: hack
        if track_ids_to_playlist is None:
            raise Exception()
        self.track_ids_to_playlist = track_ids_to_playlist
        self._isrc_seen: Set[str] = set()
        # FIXME: from config?
        self.bad_words_in_album_names = ['christmas', 'joulu']
        # FIXME: do something (emulates what autologging provides
        self.__log = logging.getLogger(__name__)

    def is_track_ok_to_add(self, track_id: str) -> bool:

        # TODO: cleanup this mess and move to new class
        # track and track_relinked may be totally different
        # isrc can be different, album can be different ...

        # NOTE: we need correct relinking information
        track_relinked = self.spotify.track(track_id, market=self.user_country)

        # NOTE: to speed up things, use relinked track as track if id matches
        if track_relinked.id == track_id:
            track = track_relinked
            relinked = False
        else:
            self.__log.warning('track:%s: relinked to track:%s', track_id, track_relinked.id)
            track = self.spotify.track(track_id, market=None)
            relinked = True

        # and long list checks
        if track.id in self.track_ids_to_playlist:
            self.__log.debug('track:%s: already added', track.id)
            return False
        elif relinked and track_relinked.id in self.track_ids_to_playlist:
            self.__log.debug('track:%s: already added (relinked)', track.id)
            return False
        # NOTE: check playable on relinked track
        elif not self.is_track_playable(track_relinked):
            self.__log.debug('track:%s: not playable', track.id)
            return False
        elif not self.is_track_album_name_good(track):
            self.__log.debug('track:%s: album name "%s" not good', track.id, track.album.name)
            return False
        elif self.is_track_isrc_already_seen(track):
            self.__log.debug('track:%s: isrc already seen', track.id)
            return False
        elif (
            relinked
            and not self.has_tracks_same_isrc(track, track_relinked)
            and self.is_track_isrc_already_seen(track_relinked)
        ):
            self.__log.debug('track:%s: isrc already seen (relinked)', track.id)
            return False
        elif self.is_track_already_played(track):
            self.__log.debug('track:%s: already played', track.id)
            return False
        elif relinked and self.is_track_already_played(track_relinked):
            self.__log.debug('track:%s: already played (relinked)', track.id)
            return False
        elif self.is_track_isrc_already_played(track):
            self.__log.debug('track:%s: isrc already played', track.id)
            return False
        elif relinked and self.is_track_isrc_already_played(track_relinked):
            self.__log.debug('track:%s: isrc already played (relinked)', track.id)
            return False
        else:
            return True

    def is_track_already_played(self, track: Track) -> bool:

        if self.spotify_history.count_by_track_id(track.uri) > 0:
            return True
        else:
            return False

    # TODO: isrc is only on FullTrack?
    def is_track_isrc_already_played(self, track: FullTrack) -> bool:

        isrc = track.external_ids.get('isrc')
        if isrc is None:
            self.__log.warning('track:%s: isrc is %s', track.id, isrc)
            return False
        if self.spotify_history.count_by_track_isrc(isrc) > 0:
            return True
        else:
            return False

    # TODO: isrc is only on FullTrack?
    # FIXME: split check and add
    def is_track_isrc_already_seen(self, track: FullTrack) -> bool:

        isrc = track.external_ids.get('isrc')
        if isrc is None:
            self.__log.warning('track:%s: isrc is %s', track.id, isrc)
            return False
        elif isrc in self._isrc_seen:
            return True
        else:
            self._isrc_seen.add(isrc)
            return False

    def has_tracks_same_isrc(self, track1: FullTrack, track2: FullTrack) -> bool:

        if track1.external_ids.get('isrc') == track2.external_ids.get('isrc'):
            return True
        else:
            self.__log.warning('track:%s and track:%s has different ISRC', track1.id, track2.id)
            return False

    def is_track_playable(self, track: FullTrack) -> bool:

        if track.is_playable is None:
            # TODO: raise exception
            self.__log.warning('%s: is_playable is None', track.id)
            return False
        else:
            return track.is_playable

    def is_track_on_market(self, track: FullTrack, market: str) -> bool:

        markets = track.available_markets
        if markets is None:
            # TODO: raise exception
            self.__log.warning('%s: available_markets is None', track.id)
            return False
        elif market in markets:
            return True
        else:
            return False

    def is_track_album_name_good(self, track: FullTrack) -> bool:

        if any(bad in track.album.name.lower() for bad in self.bad_words_in_album_names):
            return False
        else:
            return True

# END
