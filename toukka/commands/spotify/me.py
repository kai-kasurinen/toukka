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

from toukka.toukka import Toukka
from toukka.models.track_features import TrackFeaturesDelivered
from toukka.utils import json_dump, json_dump_print, format_as_table


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


@argh.named('top-tracks')
def current_user_top_tracks():
    toukka = Toukka()
    # long_term: calculated from several years
    # medium_term: aapproximately last 6 months
    # short_term: approximately last 4 weeks
    ranges = ['short_term', 'medium_term', 'long_term']

    for r in ranges:
        print("range:", r)
        results = toukka.sp.current_user_top_tracks(time_range=r, limit=50)
        for i, item in enumerate(results['items']):
            print(i+1, item['name'], '//',
                  _get_nice_string_from_artists(item['artists']))
        print()


@argh.named('top-tracks-new')
def current_user_top_tracks_new():
    toukka = Toukka()
    # long_term: calculated from several years
    # medium_term: aapproximately last 6 months
    # short_term: approximately last 4 weeks
    ranges = ['short_term', 'medium_term', 'long_term']

    for r in ranges:
        print("range", r)
        results = toukka.sp.current_user_top_tracks(time_range=r, limit=50)
        tracks = _get_tracks_dict(results['items'])
        # table = tabulate.tabulate(tracks, headers='keys', showindex='always')
        table = format_as_table(tracks, ['pos', 'name', 'artists', 'popularity'])
        print(table)


def _get_tracks_dict(items):

    tracks = []
    for i, track in enumerate(items):
        tracks.append({
            'pos': i+1,
            # 'artists': list(artist.get('name') for artist in track['artists']),
            'artists': ", ".join(artist.get('name') for artist in track['artists']),
            'name': track['name'],
            'uri': track['uri'],
            'popularity': track['popularity']
        })
    return tracks


@argh.named('top-artists')
def current_user_top_artists():
    toukka = Toukka()
    # long_term: calculated from several years
    # medium_term: aapproximately last 6 months
    # short_term: approximately last 4 weeks
    ranges = ['short_term', 'medium_term', 'long_term']
    for r in ranges:
        print("range:", r)
        results = toukka.sp.current_user_top_artists(time_range=r, limit=50)
        for i, item in enumerate(results['items']):
            print(i+1, item['name'])
        print()


@argh.named('top-artists-new')
def current_user_top_artists_new():
    toukka = Toukka()
    # long_term: calculated from several years
    # medium_term: aapproximately last 6 months
    # short_term: approximately last 4 weeks
    ranges = ['short_term', 'medium_term', 'long_term']
    for r in ranges:
        print("range:", r)
        results = toukka.sp.current_user_top_artists(time_range=r, limit=50)
        print(format_as_table(results['items'], ['name', 'popularity', 'genres']))
        print()


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

    print('total items: %s' % len(paging['items']))

    items = toukka.sp.aggregate_paging_results(paging)
    print('total agggregated items: %s' % len(items))


def _get_nice_string_from_artists(artists):
    return ", ".join("%s (%s)" % (artist.get('name'), artist.get('id')) for artist in artists)


#

COMMANDS = [current_user,
            current_user_saved_albums,
            current_user_saved_tracks,
            current_user_followed_artists,
            current_user_top_tracks,
            current_user_top_tracks_new,
            current_user_top_artists,
            current_user_top_artists_new,
            current_user_playlists,
            current_user_recently_played
            ]

# END
