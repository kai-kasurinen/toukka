#

import re
import logging
import datetime
import statistics

import iso8601
import humanize
import tabulate
import argh
import simplejson as json

from toukka.hub import Toukka
#from toukka.spotify.models.track_features import TrackFeaturesDelivered
from toukka.utils import json_dump, json_dump_print, format_as_table
from toukka.utils import _get_flags, _list_to_string


def current_user():
    toukka = Toukka()
    return json_dump(toukka.sp.me())


@argh.named('saved-albums')
def current_user_saved_albums():
    toukka = Toukka()
    return json_dump(toukka.sp.current_user_saved_albums())


@argh.named('saved-tracks')
def current_user_saved_tracks():
    toukka = Toukka()
    return json_dump(toukka.sp.current_user_saved_tracks())


@argh.named('followed-artists')
def current_user_followed_artists():
    toukka = Toukka()
    return json_dump(toukka.sp.current_user_followed_artists())




@argh.named('playlists')
def current_user_playlists():
    toukka = Toukka()

    playlists = toukka.sp.current_user_playlists()

    print("total: {}".format(
        playlists['total']))

    print()
    for playlist in playlists['items']:
        print("name: {}, number of songs: {}, playlist ID: {} ".format(
            playlist['name'],
            playlist['tracks']['total'],
            playlist['id']))


@argh.named('recently-played')
def current_user_recently_played():
    toukka = Toukka()

    paging = toukka.sp.current_user_recently_played_new(limit=50)
    # json_dump_print(paging)

    if paging.get('total'):
        print('total: %s' % paging.get['total'])

    if paging.get('cursors'):
        after = paging['cursors']['after']
        before = paging['cursors']['before']
        print('after: %s, before: %s' % (
            datetime.datetime.fromtimestamp(int(after)/1000),
            datetime.datetime.fromtimestamp(int(before)/1000)))

    #print('total items: %s' % len(paging['items']))

    items = toukka.sp.aggregate_paging_results(paging)

    for item in items:
        #json_dump_print(item)
        artists_string = _get_string_from_artists(item['track']['artists'])
        _played_at = item['played_at']

        print('{played_at} {track[name]:40} {artists_string} {context[uri]}'.
              format(**item, artists_string=artists_string))



def _get_string_from_artists_with_ids(artists):
    return ", ".join("%s (%s)" % (artist.get('name'), artist.get('id')) for artist in artists)


def _get_string_from_artists(artists):
    return ', '.join('%s' % (artist.get('name')) for artist in artists)


#

COMMANDS = [current_user,
            current_user_saved_albums,
            current_user_saved_tracks,
            current_user_followed_artists,
            current_user_playlists,
            current_user_recently_played
            ]

# END
