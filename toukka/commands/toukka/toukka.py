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

    currently_playing = toukka.sp.currently_playing()

    if not currently_playing:
        raise ConnectionError('User not connected to Spotify ')

    context = currently_playing.get('context')
    item = currently_playing.get('item')

    # status and context
    print('is playing: %s' % (currently_playing['is_playing']))
    if context:
        print('\tcontext: %s (%s)' % (context['type'], context['uri']))
    else:
        print('\tcontext: %s' % context)

    currently_playing_timestamp = datetime.datetime.fromtimestamp(
        currently_playing['timestamp']/1000.0)

    print('\ttimestamp: %s (%s)' % (
        humanize.naturaldate(currently_playing_timestamp),
        humanize.naturaltime(datetime.datetime.now() - currently_playing_timestamp)))

    if currently_playing.get('progress_ms'):
        print('\tprogress: %s' % datetime.timedelta(milliseconds=currently_playing['progress_ms']))

    if with_artist:
        artists = item['artists']
        for artist in artists:
            artist_item = toukka.sp.artist(artist['id'])
            artist_entity = toukka.sp.crowd_site_entity(artist['uri'])
            print()
            _print_artist_info(artist_item, artist_entity)

    if with_album:
        album_id = item['album']['id']
        album_uri = item['album']['uri']
        album_item = toukka.sp.album(album_id)
        album_entity = toukka.sp.crowd_site_entity(album_uri)
        print()
        _print_album_info(album_item, album_entity)

    if with_track:
        track_id = item['id']
        track_uri = item['uri']
        track_features = toukka.sp.audio_features_one(track_id)
        track_entity = toukka.sp.crowd_site_entity(track_uri)
        print()
        _print_track_info(item, track_entity, track_features, **args)


###

def _print_artist_info(artist_item, artist_entity, **kwargs):
    """"""

    artist = artist_item

    print('artist: %s (%s)' % (artist['name'], artist['id']))
    artist_genres = artist_item['genres']
    print('\tgenres: %s' % (artist_genres))
    artist_uri = artist_item['uri']
    artist_tags = artist_entity['entity'].get('tags')
    artist_external_urls = artist_entity['entity'].get('external_urls')
    print('\ttags: %s' % (artist_tags))
    artist_popularity = artist_item['popularity']
    print('\tpopularity: %s' % (artist_popularity))
    artist_followers = artist_item.get('followers').get('total')
    print('\tfollowers: %s' % (artist_followers))

    if artist_external_urls:
        print('\turls:')
        for u in artist_external_urls:
            print('\t\t%s: %s' % (u.get('name'), u.get('url')))

    artist_origin_locality = artist_entity.get('entity').get('origin_locality')
    artist_origin_country = artist_entity.get('entity').get('origin_country')
    artist_aliases = artist_entity.get('entity').get('aliases')
    artist_categories = artist_entity.get('entity').get('categories')
    print('\torigin locality: %s' % artist_origin_locality)
    print('\torigin country: %s' % artist_origin_country)
    print('\taliases: %s' % artist_aliases)
    print('\tcategories: %s' % artist_categories)
    artist_bio = artist_entity['entity'].get('bio')
    print('\tbio: %.100s ...' % _cleanhtml(artist_bio))


def _print_album_info(album_item, album_entity, **kwargs):
    """"""

    album = album_item
    album_name = album['name']
    album_type = album['album_type']
    album_id = album['id']
    album_uri = album['uri']
    album_genres = album_item['genres']
    album_popularity = album_item['popularity']
    album_release_date = album_item['release_date']
    album_release_date_precision = album_item['release_date_precision']
    album_copyrights = album_item['copyrights']
    album_markets = album_item.get('available_markets')

    if album_entity:
        album_tags = album_entity['entity'].get('tags')
        album_external_urls = album_entity['entity'].get('external_urls')
        album_categories = album_entity['entity'].get('categories')
        album_label = album_entity['entity'].get('label')
        # album_recording_copyright = album_entity['entity'].get('recording_copyright')
    else:
        logging.warning('No entity for album %s' % album_uri)

    print('album: %s (%s) (%s) (%s %s)' % (
        album_name, album_type, album_id,
        album_release_date, album_release_date_precision))

    print('\tartists: %s' % _get_nice_string_from_artists(album_item['artists']))
    print('\tgenres: %s' % (album_genres))
    print('\texternal ids: %s' % (album_item['external_ids']))
    print('\tpopularity: %s' % (album_popularity))
    print('\tmarkets: %s' % (len(album_markets)))

    if album_entity:
        print('\ttags: %s' % (album_tags))

        if album_external_urls:
            print('\turls:')
            for url in album_external_urls:
                print('\t\t%s: %s' % (url.get('name'), url.get('url')))

        print('\tcategories: %s' % (album_categories))
        print('\tlabel: %s' % (album_label))
        # print('\tcopyright: %s' % (album_recording_copyright))
        album_entity_artists = album_entity['entity']['artists']
        print('\tentity artists:')
        for artist in album_entity_artists:
            print('\t\t%s: %s (%s)' % (artist.get('role'), artist.get('name'), artist.get('id')))

    print('\tcopyrights:')
    for copyright in album_copyrights:
        print('\t\t%s: %s' % (copyright.get('type'), copyright.get('text')))


def _print_track_info(track_item, track_entity, track_features, **kwargs):
    """"""

    item = track_item

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

    print('track: %s (%s)' % (track_name, track_id))
    print('\tartists: %s' % _get_nice_string_from_artists(item['artists']))
    print('\tduration: %s' % (datetime.timedelta(milliseconds=track_duration)))

    if track_entity:
        track_entity_artists = track_entity['entity']['artists']
        print('\tentity artists:')
        for artist in track_entity_artists:
            print('\t\t%s: %s (%s)' % (artist.get('role'), artist.get('name'), artist.get('id')))

    print('\texternal ids: %s' % (item['external_ids']))
    if track_entity:
        print('\ttags: %s' % (track_tags))
    print('\tpopularity: %s' % (track_popularity))
    print('\tmarkets: %s' % (len(track_markets)))

    if track_entity and track_external_urls:
        print('\turls:')
        if track_entity:
            for u in track_external_urls:
                print('\t\t%s: %s' % (u.get('name'), u.get('url')))

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


#

def _cleanhtml(raw_html):
    if raw_html is None:
        return raw_html
    else:
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext


def _get_nice_string_from_artists(artists):
    return ", ".join("%s (%s)" % (artist.get('name'), artist.get('id')) for artist in artists)


#

COMMANDS = [playing]

# END
