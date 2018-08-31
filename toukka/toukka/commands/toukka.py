#

import re
import logging
import datetime
import statistics
import pprint

import iso8601
import humanize
import tabulate
import argh
import simplejson as json

from toukka import Toukka
from toukka.models.track_features import TrackFeaturesDelivered
from toukka.utils import json_dump, json_dump_print, format_as_table
from toukka.utils import _get_flags, _list_to_string


def playlist_info(uri):
    toukka = Toukka()

    playlist = toukka.sp.get_playlist_by_uri(uri)
    results = playlist

    #
    print('uri: %s' % results['uri'])
    print('name: %s' % results['name'])
    print('desc: %s' % results['description'])
    print('owner: %s (%s)' % (results['owner']['display_name'], results['owner']['uri']))
    print('followers: %s' % results['followers']['total'])
    print('track count: %s' % results['tracks']['total'])

    #
    flags = []
    if results['public']:
        flags.append('public')
    if results['collaborative']:
        flags.append('collaborative')
    print('flags: %s' % flags)

    # modifies results['tracks']['items']
    playlist_tracks = toukka.sp.aggregate_paging_results(results['tracks'])

    if len(playlist_tracks) != results['tracks']['total']:
        logging.warning('track count mismatch, playlist_tracks %s,  results_total,  %s',
                        len(playlist_tracks), results['tracks']['total'])

    tracks_duration = []
    tracks_added_at = []
    tracks_popularity = []
    tracks_id = []
    tracks = []

    for playlist_track in playlist_tracks:

        track_added_at = iso8601.parse_date(playlist_track['added_at'])
        tracks_added_at.append(track_added_at)

        track = playlist_track['track']

        tracks_duration.append(track['duration_ms'])
        tracks_popularity.append(track['popularity'])
        tracks_id.append(track['id'])

    print('duration: %s' % (datetime.timedelta(milliseconds=sum(tracks_duration))))
    print('added between: %s -> %s ' % (min(tracks_added_at), max(tracks_added_at)))
    print('popularity: %s - %s (mean: %s, median: %s)' % (
        min(tracks_popularity),
        max(tracks_popularity),
        statistics.mean(tracks_popularity),
        statistics.median(tracks_popularity)))

    # TODO:
    # top genres,
    # popular tracks,
    # year,
    # recently added tracks,
    # artist count,
    # repeated artists,
    # well known artists, least known artists,
    # similar artists to explore

#

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


#

def _cleanhtml(raw_html):
    if raw_html is None:
        return raw_html
    else:
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext


def _get_nice_string_from_artists(artists):
    return ", ".join("%s (%s)" % (artist.get('name'), artist.get('uri')) for artist in artists)


#

COMMANDS = [playlist_info]

# END
