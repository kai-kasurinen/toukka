#

import re
import logging
import datetime
import humanize
import iso8601
import statistics
import pprint
import argh

from toukka import Toukka
from toukka.utils import _get_flags, _list_to_string


def user_playlists_info(user):
    '''Gets playlists of a user'''
    toukka = Toukka()

    paging = toukka.sp.user_playlists(user)

    print("total playlists: {}".format(
        paging['total']))

    playlists = toukka.sp.aggregate_paging_results(paging)

    own = [p for p in playlists if p.get('owner').get('id') == user]
    public = [p for p in playlists if p.get('public') is True]
    collaborative = [p for p in playlists if p.get('collaborative') is True]

    print('total user own playlists: %s' % len(own))
    print('total public playlists: %s' % len(public))
    print('total collaborative playlists: %s' % len(collaborative))
    print('total user own playlists: %s' % len(own))


def user_playlists(user,
                   filter_own=False,
                   filter_public=False,
                   filter_collaborative=False,
                   filter_by_userid=None):
    '''Gets playlists of a user'''
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


def playlist_info(uri, dump=False, with_tracks=False):
    toukka = Toukka()
    playlist = toukka.sp.get_playlist_by_uri(uri)

    if dump:
        pprint.pprint(playlist)
        return
    else:
        _print_playlist_info(playlist)

        if with_tracks:
            playlist_tracks = toukka.sp.aggregate_paging_results(playlist['tracks'])
            _print_playlist_tracks(playlist_tracks)


def _print_playlist_info(playlist):
    print('playlist: {name} ({uri}) (followers: {followers[total]}, tracks: {tracks[total]}'.format(**playlist))
    print('\tdescription: {description}'.format(**playlist))
    print('\towner: {owner[display_name]} ({owner[id]}) ({owner[uri]})'.format(**playlist))
    print('\tsnapshot: {snapshot_id}'.format(**playlist))
    if playlist.get('external_urls'):
            print('\texternal urls: {external_urls}'.format(**playlist))
    print('\tflags: {}'.format(_list_to_string(_get_flags(playlist, ['public', 'collaborative']))))


def _print_playlist_tracks(playlist_tracks):
    line = "{track[name]}"
    for playlist_track in playlist_tracks:
        print(line.format(**playlist_track))


#
COMMANDS = [playlist_info,
            user_playlists,
            user_playlists_info]

# END
