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

    def is_track_ok_to_add(self, track: Track) -> bool:

        # TODO: more cleanup

        # first use checks that not need FullTrack
        if track.id in self.track_ids_to_playlist:
            self.__log.debug('track:%s: already added', track.id)
            return False

        if self.is_track_already_played(track):
            self.__log.debug('track:%s: already played', track.id)
            return False

        # relinked track may be totally different
        track_relinked = self.spotify.track(track.id, market=self.user_country)

        # is relinked ... (do it better)
        if track.id != track_relinked.id:
            relinked = True
            self.__log.warning('track:%s: relinked to track:%s', track.id, track_relinked.id)
        else:
            relinked = False

        # original FullTrack
        if relinked:
            # get full track if track_relinked is really relinked
            if isinstance(track, FullTrack):
                track_full = track
            else:
                track_full = self.spotify.track(track.id, market=None)
        else:
            # use relinked track if its not relinked
            track_full = track_relinked

        # check playable from relinked track
        if not self.is_track_playable(track_relinked):
            self.__log.debug('track:%s: not playable', track_relinked.id)
            return False

        if self.is_track_isrc_already_seen(track_full):
            self.__log.debug('track:%s: isrc already seen', track_full.id)
            return False

        if not self.is_track_album_name_good(track_full):
            self.__log.debug('track:%s: album name "%s" not good', track_full.id, track_full.album.name)
            return False

        if self.is_track_isrc_already_played(track_full):
            self.__log.debug('track:%s: isrc already played', track_full.id)
            return False

        # all checks that use relinked
        if relinked:

            if track_relinked.id in self.track_ids_to_playlist:
                self.__log.debug('track:%s: already added (relinked)', track_relinked.id)
                return False

            if not self.is_track_album_name_good(track_relinked):
                self.__log.debug('track:%s: album name "%s" not good',
                                 track_relinked.id, track_relinked.album.name)
                return False

            if (not self.has_tracks_same_isrc(track_full, track_relinked)
                    and self.is_track_isrc_already_seen(track_relinked)):
                self.__log.debug('track:%s: isrc already seen (relinked)', track_relinked.id)
                return False

            if self.is_track_already_played(track_relinked):
                self.__log.debug('track:%s: already played (relinked)', track_relinked.id)
                return False

            if self.is_track_isrc_already_played(track_relinked):
                self.__log.debug('track:%s: isrc already played (relinked)', track_relinked.id)
                return False

        # finally return True if all checks passed
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
