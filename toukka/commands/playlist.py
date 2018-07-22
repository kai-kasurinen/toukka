#

import argh
import re
import logging
import datetime
import humanize
import iso8601
import statistics

import simplejson as json

from ..toukka import Toukka


@argh.named('info')
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
COMMANDS = [playlist_info]
