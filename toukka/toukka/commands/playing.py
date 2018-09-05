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

from toukka import Toukka, ResourceURL
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
            self.toukka.sp2mb.feed_track_id(item.get('id'))
            self._print_musicbrainz()
            self._print_discogs()


    def _print_musicbrainz(self):
        print()
        print('MusicBrainz:')

        sp_track_uri = self.currently_playing.get('item').get('uri')
        sp_track_mbid = self.toukka.sp2mb.get_mbid(sp_track_uri)
        if sp_track_mbid:
            self._print_musicbrainz_recording(sp_track_mbid)

        sp_album_uri = self.currently_playing.get('item').get('album').get('uri')
        sp_album_mbid = self.toukka.sp2mb.get_mbid(sp_album_uri)
        if sp_album_mbid:
            self._print_musicbrainz_release(sp_album_mbid)

        for sp_artist in self.currently_playing.get('item').get('artists'):
                sp_artist_uri = sp_artist.get('uri')
                sp_artist_mbid = self.toukka.sp2mb.get_mbid(sp_artist_uri)
                if sp_artist_mbid:
                    self._print_musicbrainz_artist(sp_artist_mbid)

    def _print_discogs(self):
        print('Discogs:')

        sp_album_uri = self.currently_playing.get('item').get('album').get('uri')
        sp_album_mbid = self.toukka.sp2mb.get_mbid(sp_album_uri)
        if sp_album_mbid:
            urls = self.toukka.mb.get_release_url_relations_by_type(sp_album_mbid, 'discogs')
            for u in urls:
                self._print_discogs_release_by_url(u)


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
        # FIXME: needs get_album_tracks
        if album.get('tracks'):
            print('\ttracks: %s' % (album.get('tracks').get('total')))
        if album.get('label'):
            print('\tlabel: {label}'.format(**album))
        if album.get('copyrights'):
            print('\tcopyrights:')
            for copyright in album.get('copyrights'):
                print('\t\t{type}: {text}'.format(**copyright))

    def _print_track_info(self, track_id):
        track = self.toukka.sp.track(track_id)
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

    def _print_musicbrainz_artist(self, mbid):
        artist = self.toukka.mb.get_artist(mbid)
        print('artist: {name} ({disambiguation}) ({id})'.format(**artist))
        if artist.get('tags'):
            print('\ttags: {}'.format(self._musicbrainz_tags_to_string(artist.get('tags'))))
        if artist.get('rating').get('value'):
            print('\trating: {rating[value]} (votes: {rating[votes-count]})'.format(**artist))
        print('\turl: {}'.format(self.toukka.mb.get_entity_url('artist', artist.get('id'))))
        self._print_url_relations(self.toukka.mb.get_artist_url_relations(mbid))
        print()

    def _print_url_relations(self, relations):
        if relations:
            print('\tlinks:')
            for r in relations:
                print('\t\t{type}: {url}'.format(**r))

    def _print_musicbrainz_release(self, mbid):
        release = self.toukka.mb.get_release(mbid)
        print('release: {title} ({disambiguation}) ({id}) ({barcode}) ({date} {country})'.format(**release))
        print('\tartists: {}'.format(self._musicbrainz_artist_credit_to_string(release.get('artist-credit'))))
        if release.get('tags'):
            print('\ttags: {}'.format(self._musicbrainz_tags_to_string(release.get('tags'))))
        #print('\trelease group: {title} ({disambiguation}) ({primary-type}, {secondary-types})'.format(**release.get('release-group'))) 
        print('\turl: {}'.format(self.toukka.mb.get_entity_url('release', release.get('id'))))
        self._print_url_relations(self.toukka.mb.get_release_url_relations(mbid))
        print()
        self._print_musicbrainz_release_group(release.get('release-group').get('id'))

    def _print_musicbrainz_release_group(self, mbid):
        release_group = self.toukka.mb.get_release_group(mbid)
        print('release group: {title} ({disambiguation}) ({id}) ({primary-type}, {secondary-types}) ({first-release-date})'.format(**release_group))
        print('\tartists: {}'.format(self._musicbrainz_artist_credit_to_string(release_group.get('artist-credit'))))
        if release_group.get('tags'):
            print('\ttags: {}'.format(self._musicbrainz_tags_to_string(release_group.get('tags'))))
        if release_group.get('rating').get('value'):
            print('\trating: {rating[value]} (votes: {rating[votes-count]})'.format(**release_group))
        print('\turl: {}'.format(self.toukka.mb.get_entity_url('release-group', release_group.get('id'))))
        self._print_url_relations(self.toukka.mb.get_release_group_url_relations(mbid))
        print()

    def _print_musicbrainz_recording(self, mbid):
        recording = self.toukka.mb.get_recording(mbid)
        print('recording: {title} ({disambiguation}) ({id}) ({isrcs})'.format(**recording))
        print('\tartists: {}'.format(self._musicbrainz_artist_credit_to_string(recording.get('artist-credit'))))
        if recording.get('tags'):
            print('\ttags: {}'.format(self._musicbrainz_tags_to_string(recording.get('tags'))))
        if recording.get('rating').get('value'):
            print('\trating: {rating[value]} (votes: {rating[votes-count]})'.format(**recording))
        print('\turl: {}'.format(self.toukka.mb.get_entity_url('recording', recording.get('id'))))
        #print('\tworks: {}'.format(self.toukka.mb.get_recording_work_relations(mbid)))
        self._print_acousticbrainz_info(recording.get('id'))
        self._print_url_relations(self.toukka.mb.get_recording_url_relations(mbid))
        print()
        for work_mbid in self.toukka.mb.get_recording_work_relations(mbid):
            self._print_musicbrainz_work(work_mbid)

    def _print_musicbrainz_work(self, mbid):
        work = self.toukka.mb.get_work(mbid)
        print('work: {title} ({disambiguation}) ({id}) ({type}) ({languages}) ({iswcs})'.format(**work))
        print('\turl: {}'.format(self.toukka.mb.get_entity_url('work', work.get('id'))))
        if work.get('attributes'):
            print('\tattributes: {attributes}'.format(**work))
        if work.get('tags'):
            print('\ttags: {}'.format(self._musicbrainz_tags_to_string(work.get('tags'))))
        if work.get('rating').get('value'):
            print('\trating: {rating[value]} (votes: {rating[votes-count]})'.format(**work))
        self._print_musicbrainz_work_relations(work.get('relations'))
        #pprint.pprint(work)
        print()

    def _print_musicbrainz_work_relations(self, relations):
        for r in relations:
            if r.get('target-type') == 'artist':
                print('\t{type}: {artist[name]} ({artist[id]})'.format(**r))
            elif r.get('target-type') == 'url':
                print('\t{type}: {url[resource]}'.format(**r))
            elif r.get('target-type') == 'work':
                print('\t{type}: {attributes} {work[title]} ({work[id]})'.format(**r))
            elif r.get('target-type') == 'recording':
                pass
            elif r.get('target-type') == 'label':
                pass
            else:
                print('\t{}'.format(r))

    def _print_acousticbrainz_info(self, mbid):
        c = self.toukka.acousticbrainz.get_count(mbid)
        url = self.toukka.acousticbrainz.get_url(mbid)
        print('\tacousticbrainz: {count} entries, {url}'.format(**+c, url=url))

    def _print_discogs_release_by_url(self, url):
        self._print_discogs_release(ResourceURL(url).entity_id)

    def _print_discogs_release(self, rid):
        release = self.toukka.discogs.release(rid)
        release.refresh()
        print('release: {title} ({id}) ({country}) ({released}) ({status})'.format(**release.data))
        print('\tartists: {}'.format(release.artists))
        # release.url returns None?
        print('\turl: {uri}'.format(**release.data))
        print('\tgenres: {}'.format(release.genres))
        print('\tstyles: {}'.format(release.styles))
        print('\tidentifiers: {identifiers}'.format(**release.data))
        print()

    def _spotify_artists_to_string(self, artists):
        return ", ".join("%s (%s)" % (artist.get('name'), artist.get('uri')) for artist in artists)

    def _musicbrainz_artist_credit_to_string(self, artist_credit):
        return ", ".join("%s (%s)" % (credit.get('artist').get('name'), credit.get('artist').get('id')) for credit in artist_credit)

    def _musicbrainz_tags_to_string(self, tags):
        return ", ".join("%s (%s)" % (tag.get('name'), tag.get('count')) for tag in tags)


#

COMMANDS = [playing]

# END
