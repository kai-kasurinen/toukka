#

import logging
import click
import spotipy.convert
import enlighten
import more_itertools

import toukka.sopiva.spotify.util
import toukka.sopiva.spotify_history.util

from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.cli import cli_root

logger = logging.getLogger(__name__)


@cli_root.command()
def playlists_check():

    spotify = toukka.sopiva.spotify.util.get_spotify()

    playlists = list(spotify.all_items_from_paging(spotify.current_user_playlists(limit=50)))

    for playlist in playlists:
        logger.info(playlist.name)
        paging = spotify.playlist_tracks(playlist.id)
        tracks = list(spotify.all_items_from_paging(paging))

        if paging.total != len(tracks):
            logger.warning('paging total %s and len(tracks) %s', paging.total, len(tracks))


@cli_root.command()
@click.argument('uri')
def playlist_check(uri):

    uri_type, uri_id = spotipy.convert.from_uri(uri)

    spotify = toukka.sopiva.spotify.util.get_spotify()
    playlist = spotify.playlist(uri_id)
    paging = playlist.tracks

    logger.info(playlist.name)
    tracks = list(spotify.all_items_from_paging(paging))

    if paging.total != len(tracks):
        logger.warning('paging total %s and len(tracks) %s', paging.total, len(tracks))


# END
