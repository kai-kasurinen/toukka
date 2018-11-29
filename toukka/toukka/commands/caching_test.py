#

import argh
import re
import logging
import datetime
import humanize
import iso8601
import statistics

import simplejson as json

from toukka import Toukka
from toukka.utils import _get_flags, _list_to_string
from toukka.cache.diskcache import cache


class Playlists:
    @cache.memoize(expire=86400, typed=True)
    def user_playlists_all(self, user):
        toukka = Toukka()
        paging = toukka.sp.user_playlists(user)
        playlists = toukka.sp.aggregate_paging_results(paging)
        return playlists


def user_playlists_cached(user,
                   filter_own=False,
                   filter_public=False,
                   filter_collaborative=False,
                   filter_by_userid=None):

    toukka = Toukka()
    #paging = toukka.sp.user_playlists(user)
    #total = paging.get('total')
    #playlists = toukka.sp.aggregate_paging_results(paging)
    playlists = Playlists().user_playlists_all(user)
    total = len(playlists)


    if filter_own:
        playlists = [p for p in playlists if p.get('owner').get('id') == user]

    if filter_public:
        playlists = [p for p in playlists if p.get('public') is True]

    if filter_collaborative:
        playlists = [p for p in playlists if p.get('collaborative') is True]

    if filter_by_userid:
        playlists = [p for p in playlists if p.get('owner').get('id') == filter_by_userid]

    _print_playlists(playlists)
    print('\nfiltered to {} of total {}'.format(len(playlists), total))


def _print_playlists(playlists, one_line=True):

    if one_line:
        line = "name: {name:40} id: {id:30} owner: {owner[id]:30} tracks: {tracks[total]:5} flags: {flags}"
    else:
        line = "name: {name}\nid: {id}\nowner: {owner[id]}\nflags: {flags}\ntracks: {tracks[total]}\n"

    for playlist in playlists:
        print(line.format(
            **playlist,
            flags=_list_to_string(_get_flags(playlist, ['public', 'collaborative']))))


# 

COMMANDS = [user_playlists_cached]

# END
