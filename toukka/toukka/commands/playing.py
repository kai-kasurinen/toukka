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


def _fix_isrc(isrc):
    return isrc.upper().strip('-')


def playing_musicbrainz():
    toukka = Toukka()

    currently_playing = toukka.sp.currently_playing()
    if not currently_playing:
        raise argh.CommandError('User not connected to Spotify')

    sp_item = currently_playing.get('item')
    if sp_item is None:
        raise argh.CommandError('Currently playing not track')

    sp_track = sp_item
    sp_isrc = sp_track.get('external_ids').get('isrc')
    print('spotify playing track {}'.format(sp_isrc))
    mb_isrc = toukka.mb.get_isrc(_fix_isrc(sp_isrc))

    if mb_isrc:
        #pprint.pprint(mb_isrc)
        print('found {isrc}, recordings count {count}'.format(**mb_isrc, count=len(mb_isrc.get('recordings'))))

        for r in mb_isrc.get('recordings'):
            mb_recording = toukka.mb.get_recording(r.get('id'))
            #pprint.pprint(mb_recording)
            print('{title} ({id})'.format(**mb_recording))
    else:
        print('no isrc found at musicbrainz')

    #sp_artists = sp_item.get('artists')
    #for sp_artist in sp_artists:
    #    sp_artist_mb_urls = toukka.sp.get_external_urls(sp_artist.get('uri'), 'musicbrainz')
    #    print('spotify artist {name} ({uri}) has {} musicbrainz urls'.format(len(sp_artist_mb_urls), **sp_artist))
    #    for u in sp_artist_mb_urls:
    #        mb_artist = toukka.mb.get_artist_by_url(u)
    #        #pprint.pprint(mb_artist)
    #        print('{name}, type: {type}, gender: {gender}, id: {id}'.format(**mb_artist))

    #sp_album = sp_item.get('album')
    #sp_album_mb_urls = toukka.sp.get_external_urls(sp_album.get('uri'), 'musicbrainz')
    #print('spotify album {name} ({uri}) has {} musicbrainz urls'.format(len(sp_album_mb_urls), **sp_album))
    #for u in sp_album_mb_urls:
    #    mb_release = toukka.get_release_by_url(u)
    #    #pprint.pprint(mb_release)
    #    print('{title} ({id})'.format(**mb_release))





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
    p = PlayingPrinter(args=args)
    p.print()


class PlayingPrinter:

    def __init__(self, args={}):
        self.args = args
        self.toukka = Toukka()

    def print(self):

        # FIXME: market
        currently_playing = self.toukka.sp.currently_playing()

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

        if self.args.get('with_artist'):
            artists = item.get('artists')
            for artist in artists:
                print()
                self._print_artist_info(artist.get('id'))

        if self.args.get('with_album'):
            album = item.get('album')
            print()
            self._print_album_info(album.get('id'))

        if self.args.get('with_track'):
            print()
            self._print_track_info(item.get('id'))


    def _print_artist_info(self, artist_id):

        artist = self.toukka.sp.artist(artist_id)

        print('artist: {name} ({uri})'.format(**artist))
        print('\tgenres: {genres}'.format(**artist))
        print('\tpopularity: {popularity}'.format(**artist))
        print('\tfollowers: {followers[total]}'.format(**artist))

        if artist.get('external_ids'):
            print('\texternal ids: {external_ids}'.format(**artist))
        if artist.get('external_urls'):
            print('\texternal urls: {external_urls}'.format(**artist))


    def _print_album_info(self, album_id):

        album = self.toukka.sp.album(album_id)

        print('album: {name} ({album_type}) ({uri}) ({release_date} {release_date_precision})'.format(**album))
        print('\tartists: %s' % _get_nice_string_from_artists(album.get('artists')))

        if album.get('genres'):
            print('\tgenres: {genres}'.format(**album))
        if album.get('external_ids'):
            print('\texternal ids: {external_ids}'.format(**album))
        if album.get('external_urls'):
            print('\texternal urls: {external_urls}'.format(**album))

        if album.get('popularity'):
            print('\tpopularity: {popularity}'.format(**album))
        if album.get('available_markets'):
            print('\tmarkets: %s' % (len(album.get('available_markets'))))
        if album.get('restrictions'):
            print('\trestrictions: {restrictions}'.format(**album))

        if album.get('label'):
            print('\tlabel: {label}'.format(**album))
        if album.get('copyrights'):
            print('\tcopyrights:')
            for copyright in album.get('copyrights'):
                print('\t\t{type}: {text}'.format(**copyright))


    def _print_track_info(self, track_id):

        # FIXME: we already have this
        track = self.toukka.sp.track(track_id)
        item = track
        track_id = item.get('id')
        track_uri = item.get('uri')

        track_name = item['name']
        track_id = item['id']
        track_uri = item['uri']

        track_popularity = item['popularity']
        track_markets = item.get('available_markets')
        track_duration = item['duration_ms']

        print('track: {name} ({uri})'.format(**track))
        print('\tartists: %s' % _get_nice_string_from_artists(track.get('artists')))
        print('\tduration: %s' % (datetime.timedelta(milliseconds=track.get('duration_ms'))))
        print('\ttrack number: {track_number}, disc number: {disc_number}'.format(**track))

        if track.get('external_ids'):
            print('\texternal ids: {external_ids}'.format(**track))
        if track.get('external_urls'):
            print('\texternal urls: {external_urls}'.format(**track))
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

        if self.args.get('with_track_features'):
            self._print_track_features(track.get('id'))

    def _print_track_features(self, track_id):

        track_features = self.toukka.sp.audio_features_one(track_id)

        if track_features:

            if self.args.get('with_track_features'):
                print('\tfeatures:')
                for feature in ["acousticness", "danceability", "duration_ms",
                                "energy", "instrumentalness", "key", "liveness",
                                "loudness", "mode", "speechiness",
                                "tempo", "time_signature", "valence"]:
                    print('\t\t%s: %s' % (feature, track_features.get(feature)))

            tpdo = TrackFeaturesDelivered(track_features)
            track_features_with_delivered = tpdo.get_features_with_delivered()

            if self.args.get('with_track_delivered_features'):
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

            if self.args.get('with_track_moods'):
                track_moods = tpdo._feat_music_moods()
                print('\tmoods: %s' % (track_moods))

            if self.args.get('with_track_styles'):
                track_styles = tpdo._feat_music_styles()
                print('\tstyles: %s' % (track_styles))

            if self.args.get('with_track_key_and_mode'):
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
    return ", ".join("%s (%s)" % (artist.get('name'), artist.get('uri')) for artist in artists)


#

COMMANDS = [playing, playing_musicbrainz]

# END
