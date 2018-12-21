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

import toukka.wikidata.printer

from toukka import Toukka, ResourceURL
from toukka.spotify.models.track_features import TrackFeaturesDelivered
from toukka.utils import json_dump, json_dump_print, format_as_table
from toukka.utils import _get_flags, _list_to_string




@argh.named('playing')
def playing(with_artist: bool=True,
            with_album: bool=True,
            with_track: bool=True,
            with_track_features: bool=False,
            with_track_features_delivered: bool=False,
            with_track_moods: bool=True,
            with_track_styles: bool=True,
            with_track_key_and_mode: bool=False,
            with_musicbrainz: bool=True,
            with_discogs: bool=True,
            with_wikidata: bool=True):


    '''show information about current user playing track'''
    # pylint: disable=unused-argument, too-many-arguments

    args = locals()
    p = PlayingPrinter(args=args)
    p.print()



class PlayingPrinter:

    def __init__(self, args={}):
        # TODO: add default args
        self.args = args
        self.toukka = Toukka()

    def print(self):
        currently_playing = self.toukka.sp.currently_playing()
        self.currently_playing = currently_playing

        if not currently_playing:
            print('User not connected to Spotify or something...')
            return

        self._print_is_playing()

        track = currently_playing.get('item')

        if track is None:
            print('No track information available...')
            return

        if self.args.get('with_artist'):
            for artist_id in self._get_all_artist_ids():
                print()
                self._print_artist_info(artist_id)

        if self.args.get('with_album'):
            album = track.get('album')
            print()
            self._print_album_info(album.get('id'))

        if self.args.get('with_track'):
            print()
            self._print_track_info(track.get('id'))

        if self.args.get('with_musicbrainz'):
            print()
            self.toukka.sp2mb.feed_track_id(track.get('id'))
            self._print_musicbrainz()


    def _get_all_artist_ids(self):
        track = self.currently_playing.get('item')
        album = track.get('album')
        # FIXME: use ordered set or something
        artist_ids = set()
        for artist in track.get('artists'):
            artist_ids.add(artist.get('id'))
        for artist in album.get('artists'):
            artist_ids.add(artist.get('id'))
        return artist_ids


    def _get_track_id(self):
        return self.currently_playing.get('item').get('uri')

    def _print_history(self):
        count = self.toukka.hub.spotify_history.count_by_track_id(self._get_track_id())
        print()
        print('played count: %i' % count)

    def _print_musicbrainz(self):

        sp_track_uri = self.currently_playing.get('item').get('uri')
        sp_track_mbid = self.toukka.sp2mb.get_mbid(sp_track_uri)

        sp_album_uri = self.currently_playing.get('item').get('album').get('uri')
        sp_album_mbid = self.toukka.sp2mb.get_mbid(sp_album_uri)

        sp_artists = list()
        sp_artists += self.currently_playing.get('item').get('artists')
        sp_artists += self.currently_playing.get('item').get('album').get('artists')
        sp_artists_mbids = set()
        for sp_artist in sp_artists:
            mbid = self.toukka.sp2mb.get_mbid(sp_artist.get('uri'))
            if mbid:
                sp_artists_mbids.add(mbid)

        if (sp_track_mbid or sp_album_mbid or sp_artists_mbids):
                print()
                print('MusicBrainz:')

        if sp_track_mbid:
            self._print_musicbrainz_recording(sp_track_mbid)
        if sp_album_mbid:
            self._print_musicbrainz_release(sp_album_mbid)
        for sp_artist_mbid in sp_artists_mbids:
            self._print_musicbrainz_artist(sp_artist_mbid)

        if self.args.get('with_discogs'):
            print('Discogs:')
            if sp_album_mbid:
                urls = self.toukka.mb.get_release_url_relations_by_type(sp_album_mbid, 'discogs')
                if urls:
                    for u in urls:
                        self._print_discogs_release_by_url(u)


        if self.args.get('with_wikidata'):
            print('Wikidata:')
            if sp_artists_mbids:
                for sp_artist_mbid in sp_artists_mbids:
                    urls = self.toukka.mb.get_artist_url_relations_by_type(sp_artist_mbid, 'wikidata')
                    if urls:
                        for u in urls:
                            self._print_wikidata_by_url(u)

            if sp_album_mbid:
                    release = self.toukka.mb.get_release(sp_album_mbid)
                    release_group_mbid = release.get('release-group').get('id')
                    urls = self.toukka.mb.get_release_group_url_relations_by_type(release_group_mbid, 'wikidata')
                    if urls:
                        for u in urls:
                            self._print_wikidata_by_url(u)



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

        print('artist: {name} ({uri}) (popularity: {popularity}, followers: {followers[total]})'.format_map(artist))
        if artist.get('genres'):
            print('\tgenres: {genres}'.format_map(artist))
        #print('\tpopularity: {popularity}'.format(**artist))
        #print('\tfollowers: {followers[total]}'.format(**artist))

        if artist.get('external_urls'):
            print('\texternal urls: {external_urls}'.format(**artist))


        print('\tplayed: %s' % self.toukka.hub.spotify_history.count_by_artist_name(artist.get('name')))


    def _print_album_info(self, album_id):
        album = self.toukka.sp.album(album_id)
        print('album: {name} ({album_type}) ({uri}) ({release_date} {release_date_precision}) (popularity: {popularity}, tracks: {total_tracks})'.format(**album))
        print('\tartists: %s' % self._spotify_artists_to_string(album.get('artists')))
        if album.get('genres'):
            print('\tgenres: {genres}'.format(**album))
        if album.get('external_ids'):
            print('\texternal ids: {external_ids}'.format(**album))
        if album.get('external_urls'):
            print('\texternal urls: {external_urls}'.format(**album))
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
        track = self.toukka.sp.track(track_id)
        print('track: {name} ({uri}) (popularity: {popularity})'.format(**track))
        print('\tartists: %s' % self._spotify_artists_to_string(track.get('artists')))
        print('\talbum: {name} ({uri})'.format(**track.get('album')))
        print('\tduration: %s' % (datetime.timedelta(milliseconds=track.get('duration_ms'))))
        print('\ttrack number: {track_number}, disc number: {disc_number}'.format(**track))
        if track.get('external_ids'):
            print('\texternal ids: {external_ids}'.format(**track))
        if track.get('external_urls'):
            print('\texternal urls: {external_urls}'.format(**track))
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

        # FIXME: need check delivered too or something
        if self.args.get('with_track_features'):
            self._print_track_features(track.get('id'))

        print('\tplayed: %s' % self.toukka.hub.spotify_history.count_by_track_id(track.get('uri')))

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
        print('artist: {name} ({disambiguation}) ({id}) ({type}, {gender})'.format(**artist))
        if artist.get('area'):
            print('\tarea: {name}'.format_map(artist.get('area')))
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
        print('release: {title} ({disambiguation}) ({id}) (status: {status}) (barcode: {barcode})'.format(**release))
        print('\tartists: {}'.format(self._musicbrainz_artist_credit_to_string(release.get('artist-credit'))))
        if release.get('date'):
            print('\treleased: {date} {country}'.format_map(release))
        if release.get('media'):
            media_formats = [m.get('format') for m in release.get('media')]
            tracks_total = sum([m.get('track-count') for m in release.get('media')])
            print('\tmedia: tracks total {tracks_total}, formats: {media_formats}'.format(
                media_formats=media_formats, tracks_total=tracks_total))
        if release.get('label-info'):
            for label in release.get('label-info'):
                print('\tlabel: {label[name]} {catalog-number}'.format_map(label))
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
        count = self.toukka.acousticbrainz.get_count(mbid)
        url = self.toukka.acousticbrainz.get_url(mbid)
        if count.get('count') > 0:
            print('\tacousticbrainz: {count} entries, {url}'.format(**count, url=url))

    def _print_discogs_release_by_url(self, url):
        self._print_discogs_release(ResourceURL(url).entity_id)

    def _print_discogs_release(self, rid):
        release = self.toukka.discogs.release(rid)
        release.refresh()
        print('release: {title} ({id}) ({released}) ({status})'.format_map(release.data))
        print('\tartists: {}'.format(self._discogs_artists_to_string(release.artists)))
        if release.country:
            print('\tcountry: {}'.format(release.country))
        # release.url returns None?
        print('\turl: {uri}'.format_map(release.data))
        print('\tgenres: {}'.format(release.genres))
        print('\tstyles: {}'.format(release.styles))
        if release.data.get('identifiers'):
            print('\tidentifiers: {identifiers}'.format(**release.data))
        print()

    def _spotify_artists_to_string(self, artists):
        return ", ".join("%s (%s)" % (artist.get('name'), artist.get('uri')) for artist in artists)

    def _musicbrainz_artist_credit_to_string_with_ids(self, artist_credit):
        return ", ".join("%s (%s)" % (credit.get('artist').get('name'), credit.get('artist').get('id')) for credit in artist_credit)

    def _musicbrainz_artist_credit_to_string(self, artist_credit):
        return ''.join(c.get('name') + c.get('joinphrase') for c in artist_credit)

    def _musicbrainz_tags_to_string(self, tags):
        return ", ".join("%s (%s)" % (tag.get('name'), tag.get('count')) for tag in tags if tag.get('count') > 0)

    def _discogs_artists_to_string(self, artists):
        return ", ".join("%s (%s)" % (artist.name, artist.id) for artist in artists)

    def _print_wikidata_by_url(self, url):
        self._print_wikidata_entity(ResourceURL(url).entity_id)

    def _print_wikidata_entity(self, entity_id):
        entity = self.toukka.hub.wikidata.get(entity_id, load=True)
        toukka.wikidata.printer.print_entity(entity)


#

COMMANDS = [playing]

# END
