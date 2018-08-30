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

from toukka import Toukka
from toukka.models.track_features import TrackFeaturesDelivered
from toukka.utils import json_dump, json_dump_print, format_as_table
from toukka.utils import _get_flags, _list_to_string




@argh.named('playing')
def playing(with_artist=True,
            with_album=True,
            with_track=True,
            with_track_features=False,
            with_track_features_delivered=False,
            with_track_moods=True,
            with_track_styles=True,
            with_track_key_and_mode=False):
    """show information about current user playing track"""
    # pylint: disable=unused-argument, too-many-arguments

    args = locals()

    toukka = Toukka()

    # FIXME: market
    currently_playing = toukka.sp.currently_playing()

    if not currently_playing:
        raise argh.CommandError('User not connected to Spotify')

    context = currently_playing.get('context')
    item = currently_playing.get('item')

    # status and context
    print('is playing: %s' % (currently_playing['is_playing']))
    if context:
        print('\tcontext: {type}, {uri}'.format(**context))
    else:
        print('\tcontext: %s' % context)

    currently_playing_timestamp = datetime.datetime.fromtimestamp(
        currently_playing['timestamp']/1000.0)

    print('\ttimestamp: %s (%s)' % (
        humanize.naturaldate(currently_playing_timestamp),
        humanize.naturaltime(datetime.datetime.now() - currently_playing_timestamp)))

    if currently_playing.get('progress_ms'):
        print('\tprogress: %s' % datetime.timedelta(milliseconds=currently_playing['progress_ms']))

    if item is None:
        print('item is None')
        return

    if with_artist:
        artists = item.get('artists')
        for artist in artists:
            artist_item = toukka.sp.artist(artist.get('id'))
            artist_entity = toukka.sp.crowd_site_entity(artist.get('uri'))
            print()
            _print_artist_info(artist_item, artist_entity)

    if with_album:
        album = item.get('album')
        album_id = album.get('id')
        album_uri = album.get('uri')
        album_item = toukka.sp.album(album_id)
        album_entity = toukka.sp.crowd_site_entity(album_uri)
        print()
        _print_album_info(album_item, album_entity)

    if with_track:
        track_id = item.get('id')
        track_uri = item.get('uri')
        track_features = toukka.sp.audio_features_one(track_id)
        track_entity = toukka.sp.crowd_site_entity(track_uri)
        print()
        _print_track_info(item, track_entity, track_features, **args)


###

def _print_artist_info(artist_item, artist_entity, **kwargs):
    """"""

    artist = artist_item
    entity = artist_entity.get('entity')

    print('artist: {name} ({uri})'.format(**artist))
    print('\tgenres: {genres}'.format(**artist))
    print('\ttags: {tags}'.format(**entity))
    print('\tpopularity: {popularity}'.format(**artist))
    print('\tfollowers: {followers[total]}'.format(**artist))

    if entity.get('external_urls'):
        print('\turls:')
        for url in entity.get('external_urls'):
            print('\t\t{name}: {url}'.format(**url))

    print('\torigin: {origin_locality}, {origin_country[code]}'.format(**entity))

    if entity.get('aliases'):
        print('\taliases: {aliases}'.format(**entity))
    if entity.get('categories'):
        print('\tcategories: {categories}'.format(**entity))
    if entity.get('bio'):
        print('\tbio: %.100s ...' % _cleanhtml(entity.get('bio')))


def _print_album_info(album_item, album_entity, **kwargs):
    """"""

    album = album_item
    entity = album_entity.get('entity')

    print('album: {name} ({album_type}) ({uri}) ({release_date} {release_date_precision})'.format(**album))
    print('\tartists: %s' % _get_nice_string_from_artists(album.get('artists')))

    if album.get('genres'):
        print('\tgenres: {genres}'.format(**album))
    if album.get('external_ids'):
        print('\texternal ids: {external_ids}'.format(**album))
    if album.get('popularity'):
        print('\tpopularity: {popularity}'.format(**album))
    if album.get('available_markets'):
        print('\tmarkets: %s' % (len(album.get('available_markets'))))
    if album.get('restrictions'):
        print('\trestrictions: {restrictions}'.format(**album))

    if entity:
        if entity.get('tags'):
            print('\ttags: {tags}'.format(**entity))
        if entity.get('categories'):
            print('\tcategories: {categories}'.format(**entity))
        if entity.get('label'):
            print('\tlabel: {label}'.format(**entity))
        if entity.get('artists'):
            print('\tentity artists:')
            for artist in entity.get('artists'):
                print('\t\t{role}: {name} ({uri})'.format(**artist))
        if entity.get('external_urls'):
            print('\turls:')
            for url in entity.get('external_urls'):
                print('\t\t{name}: {url}'.format(**url))
    else:
        logging.warning('No entity for album %s' % album_uri)

    if album.get('copyrights'):
        print('\tcopyrights:')
        for copyright in album.get('copyrights'):
            print('\t\t{type}: {text}'.format(**copyright))


def _print_track_info(track_item, track_entity, track_features, **kwargs):
    """"""

    track = track_item
    item = track_item
    entity = track_entity.get('entity')

    track_name = item['name']
    track_id = item['id']
    track_uri = item['uri']

    if track_entity:
        track_tags = track_entity['entity'].get('tags')
        track_external_urls = track_entity['entity']['external_urls']
    else:
        logging.warning('No entity for track %s' % track_uri)

    track_popularity = item['popularity']
    track_markets = item.get('available_markets')
    track_duration = item['duration_ms']

    print('track: {name} ({uri})'.format(**track))
    print('\tartists: %s' % _get_nice_string_from_artists(track.get('artists')))
    print('\tduration: %s' % (datetime.timedelta(milliseconds=track.get('duration_ms'))))

    if entity:
        if entity.get('artists'):
            print('\tentity artists:')
            for artist in entity.get('artists'):
                print('\t\t{role}: {name} ({uri})'.format(**artist))
        if entity.get('external_urls'):
            print('\turls:')
            for url in entity.get('external_urls'):
                print('\t\t{name}: {url}'.format(**url))
        if entity.get('tags'):
            print('\ttags: {tags}'.format(**entity))
        if entity.get('categories'):
            print('\tcategories: {categories}'.format(**entity))

    if track.get('external_ids'):
        print('\texternal ids: {external_ids}'.format(**track))
    if track.get('popularity'):
        print('\tpopularity: {popularity}'.format(**track))
    if track.get('available_markets'):
        print('\tmarkets: %s' % (len(track.get('available_markets'))))
    if track.get('linked_from'):
        linked_track = track.get('linked_from')
        print('\tlinked from: {uri}'.format(**linked_track))
    if track.get('restrictions'):
        print('\trestrictions: {restrictions}'.format(**track))

    flags = _get_flags(track, ['explicit', 'is_playable', 'is_local'])
    if flags:
        print('\tflags: %s' % flags)

    if track_features:
        _print_track_features(track_features, **kwargs)


def _print_track_features(track_features, **kwargs):

    if track_features:

        if kwargs.get('with_track_features'):
            print('\tfeatures:')
            for feature in ["acousticness", "danceability", "duration_ms",
                            "energy", "instrumentalness", "key", "liveness",
                            "loudness", "mode", "speechiness",
                            "tempo", "time_signature", "valence"]:
                print('\t\t%s: %s' % (feature, track_features.get(feature)))

        tpdo = TrackFeaturesDelivered(track_features)
        track_features_with_delivered = tpdo.get_features_with_delivered()

        if kwargs.get('with_track_delivered_features'):
            # https://github.com/plamere/OrganizeYourMusic/blob/master/web/index.html#L1634
            track_sadness = track_features_with_delivered.get('sadness')
            track_happiness = track_features_with_delivered.get('happiness')
            track_anger = track_features_with_delivered.get('anger')
            track_boringness = track_features_with_delivered.get('boringness')

            print('\tdelivered features:')
            print('\t\tsadness: %s' % (track_sadness))
            print('\t\thappiness: %s' % (track_happiness))
            print('\t\tanger: %s' % (track_anger))
            print('\t\tboringness: %s' % (track_boringness))

        if kwargs.get('with_track_moods'):
            track_moods = tpdo._feat_music_moods()
            print('\tmoods: %s' % (track_moods))

        if kwargs.get('with_track_styles'):
            track_styles = tpdo._feat_music_styles()
            print('\tstyles: %s' % (track_styles))

        if kwargs.get('with_track_key_and_mode'):
            track_key = tpdo._feat_music_key_to_string()
            track_mode = tpdo._feat_music_mode_to_string()
            print('\tkey: %s' % (track_key))
            print('\tmode: %s' % (track_mode))

    else:
        logging.warning('No audio features for track %s' % track_uri)


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

COMMANDS = [playing, playlist_info]

# END
