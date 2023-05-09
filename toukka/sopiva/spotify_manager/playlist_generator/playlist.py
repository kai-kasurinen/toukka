#

from typing import Union, List

import logging
import uuid

import more_itertools
import toukka.config

from toukka.sopiva.spotify.util import (get_spotify, Spotify)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: cleanup or remove?

class PlaylistModifier:

    def __init__(self,
                 uri: str = None,
                 spotify: Spotify = None,
                 market: str = None,
                 ) -> None:

        self.spotify = spotify or get_spotify()
        self.playlist_uri = uri or _get_playlist_uri_from_config()
        self.market = market

        uri_type, uri_id = self.spotify.convert.from_uri(self.playlist_uri)
        self.playlist_id = uri_id

        # defaults
        self.playlist_name = '< g e n e r a t e d >'
        self.playlist_description = '<empty>'
        self.playlist_cleared = False
        self.playlist_details_updated = False

        self.playlist_load()

    @property
    def description(self) -> str:
        return self.playlist_description

    @description.setter
    def description(self, value: str):
        self.playlist_description = value

    def playlist_clear(self) -> None:
        self.spotify.playlist_clear(self.playlist.id)
        self.playlist_cleared = True
        logger.debug('playlist cleared')

    def playlist_load(self) -> None:
        self.playlist = self.spotify.playlist(self.playlist_id, market=self.market)
        self.playlist_snapshot_id = self.playlist.snapshot_id
        self.playlist_id = self.playlist.id

    def playlist_add_items(self, uris: List) -> None:
        self.playlist_snapshot_id = self.spotify.playlist_add(self.playlist_id, uris)

    def playlist_details_update(self) -> None:

        if self.playlist_description is None:
            logger.warning('playlist description is None')

        logger.debug(
            'playlist details update: name: %s, desc: %s',
            self.playlist_name, self.playlist_description)

        self.spotify.playlist_change_details(
            self.playlist.id,
            name=self.playlist_name,
            description=self.playlist_description)

        self.playlist_details_updated = True

    def commit(self, uris_to_playlist, dry_run) -> None:

        if len(uris_to_playlist) == 0:
            logger.info('No items to add. Try something else?')
            return

        if not dry_run and not self.playlist_cleared:
            self.playlist_clear()

        if not dry_run and not self.playlist_details_updated:
            self.playlist_details_update()

        if not dry_run:
            self.playlist_add_items(uris_to_playlist)
            logger.info('done')

        # END


# TODO: move?
def _get_playlist_uri_from_config() -> str:
    return toukka.config.lazy_config['spotify_manager']['playlist_generator']['playlist_uri'].get()


# END
