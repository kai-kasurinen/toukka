#

import re
import logging
import datetime
import humanize
import iso8601
import statistics
import pprint
import click

from toukka.util import _get_flags, _list_to_string
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.group()
def playlist():
    pass


# FIXME: should be same as user_playlists?
@playlist.command()
def current_user_playlists():
    '''get current user playlists'''

    spotify = get_spotify()
    paging = spotify.current_user_playlists(limit=50)
    print(f'user has {paging.total} playlists')

    for playlist in spotify.all_items(paging):
        printer(playlist)


# FIXME: move
@playlist.command()
@click.argument('user')
def user_playlists_info(user):
    '''gets playlists of a user'''

    spotify = get_spotify()
    paging = spotify.playlists(user, limit=50)
    print(f'user has {paging.total} playlists')
    playlists = spotify.all_items(paging)

    own = [p for p in playlists if p.owner.id == user]
    public = [p for p in playlists if p.public is True]
    collaborative = [p for p in playlists if p.collaborative is True]

    print(f'total user own playlists: {len(own)}')
    print(f'total public playlists: {len(public)}')
    print(f'total collaborative playlists: {len(collaborative)}')


@playlist.command()
@click.argument('user')
def user_playlists(user):
    spotify = get_spotify()
    paging = spotify.playlists(user, limit=50)
    print(f'user has {paging.total} playlists')
    for playlist in spotify.all_items(paging):
        printer(playlist)


@playlist.command(name='info')
@click.argument('uri')
@click.option('--market')
def playlist_info(uri: str,
                  market: str = None,
                  print_tracks: bool = False):
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    playlist = spotify.playlist(
        playlist_id=uri_id,
        market=market)
    print(type(playlist))
    printer(playlist)

    if print_tracks:
        playlist_tracks = spotify.all_items(playlist.tracks)
        for playlist_track in playlist_tracks:
            printer(playlist_track)
            track = playlist_track.track
            printer(track)


@playlist.command(name='tracks')
@click.argument('uri')
@click.option('--market')
def playlist_tracks(uri: str,
                    market: str = None):
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    playlist_tracks_paging = spotify.playlist_items(
        playlist_id=uri_id,
        market=market)
    playlist_tracks = spotify.all_items(playlist_tracks_paging)
    for playlist_track in playlist_tracks:
        printer(playlist_track)
        track = playlist_track.track
        printer(track)


# END
