#

from typing import Union, List

import logging
import textwrap

# import autologging
import more_itertools

import tekore
import tekore.convert
import toukka.config

from toukka.sopiva.spotify.util import get_spotify


# @autologging.traced
# @autologging.logged
class PlaylistModifier:

    def __init__(self,
                 uri: str = None,
                 spotify: tekore.Spotify = None,
                 market: str = None
                 ) -> None:

        self.spotify = spotify or get_spotify()
        self.playlist_uri = uri or _get_playlist_uri_from_config()
        self.market = market

        uri_type, uri_id = tekore.convert.from_uri(self.playlist_uri)
        self.playlist = self.spotify.playlist(uri_id, market=self.market)
        self.playlist_snapshot_id = self.playlist.snapshot_id

        # defaults
        self.playlist_name = '< g e n e r a t e d >'
        # NOTE: not None -> get updated. '' -> fails
        self.playlist_description = '<empty>'
        # FIXME: remove
        self.__log = logging.getLogger(__name__)

    @property
    def description(self) -> str:
        return self.playlist_description

    @description.setter
    def description(self, value: str):
        self.playlist_description = value

    def clear(self) -> None:
        self.spotify.playlist_tracks_replace(self.playlist.id, [])

    def reload(self) -> None:
        self.playlist = self.spotify.playlist(self.playlist.id)

    def tracks_add(self, track_ids: List) -> None:
        chunks = more_itertools.chunked(track_ids, 100)
        for chunk in chunks:
            self.playlist_snapshot_id = self.spotify.playlist_tracks_add(self.playlist.id, chunk)

    def details_update(self) -> None:
        if self.playlist_description is None:
            self.__log.warning('playlist description is None')
        # spotify api silently fails if description is too long
        self.playlist_description = textwrap.shorten(self.playlist_description, width=300)
        self.__log.debug(
            'playlist details update: name: %s, desc: %s',
            self.playlist_name, self.playlist_description)
        self.spotify.playlist_change_details(
            self.playlist.id,
            name=self.playlist_name,
            description=self.playlist_description)


#

def _get_playlist_uri_from_config() -> str:
    return toukka.config.lazy_config['spotify_manager']['playlist_generator']['playlist_uri'].get()


# END
