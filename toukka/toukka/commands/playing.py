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


@argh.named('playing')
def playing(with_artist=True,
            with_album=True,
            with_track=True,
            with_track_features=False,
            with_track_features_delivered=False,
            with_track_moods=True,
            with_track_styles=True,
            with_track_key_and_mode=False,
            with_musicbrainz=True):
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
        currently_playing = self.toukka.sp.currently_playing()
        self.currently_playing = currently_playing

        if not currently_playing:
            print('User not connected to Spotify or something...')
            return

        self._print_is_playing()

        item = currently_playing.get('item')

        if item is None:
            print('No track information available...')
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

        if self.args.get('with_musicbrainz'):
            print()
            self._search_from_musicbrainz()

    def _print_is_playing(self):
        currently_playing = self.currently_playing
        context = currently_playing.get('context')

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

    def _print_artist_info(self, artist_id):

        artist = self.toukka.sp.artist(artist_id)

        print('artist: {name} ({uri}) (popularity: {popularity}, followers: {followers[total]})'.format(**artist))
        print('\tgenres: {genres}'.format(**artist))
        #print('\tpopularity: {popularity}'.format(**artist))
        #print('\tfollowers: {followers[total]}'.format(**artist))

        if artist.get('external_urls'):
            print('\texternal urls: {external_urls}'.format(**artist))

    def _print_album_info(self, album_id):

        album = self.toukka.sp.album(album_id)
        self.album = album

        print('album: {name} ({album_type}) ({uri}) ({release_date} {release_date_precision})'.format(**album))
        print('\tartists: %s' % self._spotify_artists_to_string(album.get('artists')))

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
        print('\tartists: %s' % self._spotify_artists_to_string(track.get('artists')))
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

        # FIXME:
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
            logging.warning('No audio features for track %s' % track_id)

    def _search_from_musicbrainz(self):
        self._search_recording_isrc_from_musicbrainz()
        print()
        self._search_album_upc_from_musicbrainz()
        print()
        self._search_artists_urls_from_musicbrainz()
        print()
        self._search_album_url_from_musicbrainz(self.album)
        print()
        self._search_track_url_from_musicbrainz(self.currently_playing.get('item'))
        print()

    def _print_musicbrainz_artist(self, mbid):
        artist = self.toukka.mb.get_artist(mbid)
        print('artist: {name} ({disambiguation}) ({id})'.format(**artist))
        print('\ttags: {tags}'.format(**artist))
        print('\turl: {}'.format(self.toukka.mb.get_entity_url('artist', artist.get('id'))))

    def _print_musicbrainz_release(self, mbid):
        release = self.toukka.mb.get_release(mbid)
        print('release: {title} ({disambiguation}) ({id}) ({barcode}) ({date} {country})'.format(**release))
        print('\tartists: {}'.format(self._musicbrainz_artist_credit_to_string(release.get('artist-credit'))))
        print('\ttags: {tags}'.format(**release))
        print('\turl: {}'.format(self.toukka.mb.get_entity_url('release', release.get('id'))))

    def _print_musicbrainz_recording(self, mbid):
        recording = self.toukka.mb.get_recording(mbid)
        print('recording: {title} ({disambiguation}) ({id})'.format(**recording))
        print('\tartists: {}'.format(self._musicbrainz_artist_credit_to_string(recording.get('artist-credit'))))
        print('\ttags: {tags}'.format(**recording))
        print('\turl: {}'.format(self.toukka.mb.get_entity_url('recording', recording.get('id'))))

    def _search_recording_isrc_from_musicbrainz(self):
        sp_track = self.currently_playing.get('item')
        sp_isrc = sp_track.get('external_ids').get('isrc')
        print('Spotify playing track with ISRC {}'.format(sp_isrc))
        mb_isrc = self.toukka.mb.get_isrc(_fix_isrc(sp_isrc))

        if mb_isrc:
            #pprint.pprint(mb_isrc)
            print('Found {isrc}, recordings count {count}'.format(**mb_isrc, count=len(mb_isrc.get('recordings'))))

            for r in mb_isrc.get('recordings'):
                self._print_musicbrainz_recording(r.get('id'))
        else:
            print('Not found any matching ISRCs from musicbrainz')

    def _search_album_upc_from_musicbrainz(self):
        sp_album = self.album
        sp_upc = sp_album.get('external_ids').get('upc')
        print('Spotify playing album with UPC {}'.format(sp_upc))
        result = self.toukka.mb.search_releases_with_upc(sp_upc)
        print('Found {count} releases from musicbrainz'.format(**result))
        #pprint.pprint(result)
        for r in result.get('releases'):
            self._print_musicbrainz_release(r.get('id'))

    def _search_artists_urls_from_musicbrainz(self):
        artists = self.currently_playing.get('item').get('artists')
        for artist in artists:
            self._search_artist_url_from_musicbrainz(artist)

    def _search_artist_url_from_musicbrainz(self, artist):
        url = artist.get('external_urls').get('spotify')
        print('Searching artist ({name}) from musicbrainz by url'.format(**artist))
        result = self.toukka.mb.browse_urls(url)
        if result:
            #pprint.pprint(result)
            print('Found {} relations from musicbrainz'.format(len(result.get('relations'))))
            for relation in result.get('relations'):
                self._print_musicbrainz_artist(relation.get('artist').get('id'))
        else:
            print('Not found')

    def _search_album_url_from_musicbrainz(self, album):
        url = album.get('external_urls').get('spotify')
        print('Searching album ({name}) from musicbrainz by url'.format(**album))
        result = self.toukka.mb.browse_urls(url)
        if result:
            #pprint.pprint(result)
            print('Found {} relations from musicbrainz'.format(len(result.get('relations'))))
            for relation in result.get('relations'):
                self._print_musicbrainz_release(relation.get('release').get('id'))
        else:
            print('Not found')

    def _search_track_url_from_musicbrainz(self, track):
        url = track.get('external_urls').get('spotify')
        print('Searching track ({name}) from musicbrainz by url'.format(**track))
        result = self.toukka.mb.browse_urls(url)
        if result:
            #pprint.pprint(result)
            print('Found {} relations from musicbrainz'.format(len(result.get('relations'))))
            for relation in result.get('relations'):
                self._print_musicbrainz_recording(relation.get('recording').get('id'))
        else:
            print('Not found')

    def _spotify_artists_to_string(self, artists):
        return ", ".join("%s (%s)" % (artist.get('name'), artist.get('uri')) for artist in artists)

    def _musicbrainz_artist_credit_to_string(self, artist_credit):
        return ", ".join("%s (%s)" % (credit.get('artist').get('name'), credit.get('artist').get('id')) for credit in artist_credit)


#

COMMANDS = [playing]

# END
