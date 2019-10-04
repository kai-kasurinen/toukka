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

from toukka.sopiva.spotify.util import get_spotify


# FIXME: remove
from toukka.hub import Toukka
#from toukka.spotify.models.track_features import TrackFeaturesDelivered
from toukka.util import json_dump, json_dump_print, format_as_table
from toukka.util import _get_flags, _list_to_string


def current_user():
    '''get current user information'''
    # FIXME: TypeError: __init__() got an unexpected keyword argument 'birthdate'
    return get_spotify().current_user().pprint()


@argh.named('followed-artists')
def current_user_followed_artists():
    toukka = Toukka()
    return json_dump(toukka.sp.current_user_followed_artists())



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
            current_user_followed_artists,
            current_user_recently_played
            ]

# END
