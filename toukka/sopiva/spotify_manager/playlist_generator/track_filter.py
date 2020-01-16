#

from typing import List, Set, Generator, Union

import logging
import spotipy

from spotipy.model.track import FullTrack, Track
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history

from .banner import UriBanDict


class TrackFilter:

    def __init__(self,
                 spotify: spotipy.Spotify = None,
                 user_country: str = None
                 ) -> None:
        self.spotify = spotify or get_spotify()
        self.spotify_history = get_spotify_history()
        self.user_country = user_country
        # seen
        self.seen_track_id: Set[str] = set()
        self.seen_track_isrc: Set[str] = set()
        #
        self.uriban = UriBanDict()
        # FIXME: move
        self.bad_words_in_album_names = ['christmas', 'joulu']
        self.bad_words_in_track_names = ['christmas', 'joulu', 'commentary', 'what child is this']
        # TODO: add filter
        self.various_artists_uri = 'spotify:artist:0LyfQWJT6nXafLPZqxe9Of'
        # FIXME: do something (emulates what autologging provides)
        self.__log = logging.getLogger(__name__)
        self.__log.setLevel(logging.DEBUG)

    def is_track_ok_to_add(self, track: Track) -> bool:

        # TODO: more cleanup

        # first checks not need FullTrack
        if self.is_track_already_seen(track):
            self.__log.debug('track:%s: already seen', track.id)
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
        if isinstance(track, FullTrack):
            # TODO: track can be relinked, so check it before use it
            track_full = track
        else:
            if not relinked:
                # use relinked track cos it's not relinked
                track_full = track_relinked
            else:
                # we need get it
                track_full = self.spotify.track(track.id, market=None)

        # check playable from relinked track
        if not self.is_track_playable(track_relinked):
            self.__log.debug('track:%s: not playable', track_relinked.id)
            return False

        if self.is_banned(track_full):
            self.__log.debug('track:%s: banned', track_full.id)
            return False

        if not self.is_track_name_good(track_full):
            self.__log.debug('track:%s: track name "%s" not good', track_full.id, track_full.name)
            return False

        if not self.is_track_album_name_good(track_full):
            self.__log.debug('track:%s: album name "%s" not good', track_full.id, track_full.album.name)
            return False

        if self.is_track_isrc_already_seen(track_full):
            self.__log.debug('track:%s: isrc already seen', track_full.id)
            return False

        if self.is_track_isrc_already_played(track_full):
            self.__log.debug('track:%s: isrc already played', track_full.id)
            return False

        # all checks that use relinked
        if relinked:

            if self.is_banned(track_relinked):
                self.__log.debug('track:%s: banned', track_relinked.id)
                return false

            if self.is_track_already_seen(track_relinked):
                self.__log.debug('track:%s: already seen (relinked)', track_relinked.id)
                return False

            if not self.is_track_name_good(track_relinked):
                self.__log.debug('track:%s: track name "%s" not good (relinked)',
                                 track_relinked.id, track_relinked.name)
                return False

            if not self.is_track_album_name_good(track_relinked):
                self.__log.debug('track:%s: album name "%s" not good (relinked)',
                                 track_relinked.id, track_relinked.album.name)
                return False

            if self.is_track_already_played(track_relinked):
                self.__log.debug('track:%s: already played (relinked)', track_relinked.id)
                return False

            if self.has_tracks_different_isrc(track_relinked, track_full):

                if self.is_track_isrc_already_seen(track_relinked):
                    self.__log.debug('track:%s: isrc already seen (relinked)', track_relinked.id)
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

    def is_track_already_seen(self, track: Track) -> bool:

        if track.id in self.seen_track_id:
            return True
        else:
            self.seen_track_id.add(track.id)
            return False

    def is_track_isrc_already_seen(self, track: FullTrack) -> bool:

        isrc = track.external_ids.get('isrc')
        if isrc is None:
            self.__log.warning('track:%s: isrc is %s', track.id, isrc)
            return False
        elif isrc in self.seen_track_isrc:
            return True
        else:
            self.seen_track_isrc.add(isrc)
            return False

    def has_tracks_different_isrc(self, track1: FullTrack, track2: FullTrack) -> bool:

        if track1.external_ids.get('isrc') == track2.external_ids.get('isrc'):
            return False
        else:
            self.__log.warning('track:%s and track:%s has different ISRC', track1.id, track2.id)
            return True

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

        for bad_word in self.bad_words_in_album_names:
            if bad_word in track.album.name.lower():
                self.uriban.add(track.album.uri, reason=f'album_name, contains {bad_word}')
                return False

        return True

    def is_track_name_good(self, track: FullTrack) -> bool:

        for bad_word in self.bad_words_in_track_names:
            if bad_word in track.name.lower():
                self.uriban.add(track.album.uri, reason=f'track_name, contains {bad_word}')
                return False
        return True

    def is_banned(self, track: FullTrack) -> bool:

        if track.uri in self.uriban:
            self.__log.debug('%s: banned (skipping)', track.uri)
            return True
        if track.album.uri in self.uriban:
            self.__log.debug('%s: banned (skipping)', track.album.uri)
            return True
        return False

# END
