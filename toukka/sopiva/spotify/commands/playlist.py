#

import re
import logging
import datetime
import humanize
import iso8601
import statistics
import pprint
import click

import spotipy.convert

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
    paging = spotify.current_user_playlists()
    print(f'user has {paging.total} playlists')
    playlists = spotify.all_items_from_paging(paging)

    for p in playlists:
        # FIXME: better printing
        print(f'name: {p.name}',
              f', number of songs: {p.tracks.total}',
              f', id: {p.id}')


# FIXME: move
@playlist.command()
def user_playlists_info(user):
    '''gets playlists of a user'''

    spotify = get_spotify()
    paging = spotify.playlists(user)
    print(f'user has {paging.total} playlists')
    playlists = spotify.items_from_paging(paging)

    own = [p for p in playlists if p.owner.id == user]
    public = [p for p in playlists if p.public is True]
    collaborative = [p for p in playlists if p.collaborative is True]

    print(f'total user own playlists: {len(own)}')
    print(f'total public playlists: {len(public)}')
    print(f'total collaborative playlists: {len(collaborative)}')


# FIXME: fix and move
@playlist.command()
def user_playlists(user,
                   filter_own=False,
                   filter_public=False,
                   filter_collaborative=False,
                   filter_by_userid=None):
    '''gets playlists of a user'''
    toukka = Toukka()

    paging = toukka.sp.user_playlists(user)
    playlists = toukka.sp.aggregate_paging_results(paging)
    #playlists = toukka.sp.user_playlists_all(user)


    if filter_own:
        playlists = [p for p in playlists if p.get('owner').get('id') == user]

    if filter_public:
        playlists = [p for p in playlists if p.get('public') is True]

    if filter_collaborative:
        playlists = [p for p in playlists if p.get('collaborative') is True]

    if filter_by_userid:
        playlists = [p for p in playlists if p.get('owner').get('id') == filter_by_userid]

    _print_playlists(playlists)
    print('\nfiltered to {} of total {}'.format(len(playlists), paging.get('total')))


def _print_playlists(playlists, one_line=True):

    if one_line:
        line = "name: {name:40} id: {id:30} owner: {owner[id]:30} tracks: {tracks[total]:5} flags: {flags}"
    else:
        line = "name: {name}\nid: {id}\nowner: {owner[id]}\nflags: {flags}\ntracks: {tracks[total]}\n"

    for playlist in playlists:
        print(line.format(
            **playlist,
            flags=_list_to_string(_get_flags(playlist, ['public', 'collaborative']))))


@playlist.command(name='info')
@click.argument('uri')
@click.option('--market')
def playlist_info(uri: str,
                  market: str = None,
                  print_tracks: bool = False):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    playlist = spotify.playlist(playlist_id=uri_id, market=market)
    printer(playlist)

    if print_tracks:
        playlist_tracks = spotify.all_items_from_paging(playlist.tracks)
        for playlist_track in playlist_tracks:
            printer(playlist_track)
            track = playlist_track.track
            printer(track)


@playlist.command(name='tracks')
@click.argument('uri')
@click.option('--market')
def playlist_tracks(uri: str,
                    market: str = None):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    playlist_tracks_paging = spotify.playlist_tracks(playlist_id=uri_id, market=market)
    playlist_tracks = spotify.all_items_from_paging(playlist_tracks_paging)
    for playlist_track in playlist_tracks:
        track = playlist_track.track
        printer(track)


# END
