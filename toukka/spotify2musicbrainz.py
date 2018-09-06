#

import logging
import shelve
import pprint
import unicodedata
import datetime
import functools
import fuzzywuzzy.fuzz
import unidecode

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Spotify2MusicBrainz:
    def __init__(self, dbfile=None, hub=None):
        if not dbfile:
            raise Exception()
        if not hub:
            raise Exception()
        self.db = shelve.open(dbfile)
        self.hub = hub
        # FIXME:
        self.toukka = self.hub
        # FIXME: temporary
        #self._remove_bad_data_from_db()
        self.search_modes = ['strict', 'fuzzy']

    def get_mbid(self, uri):
        mbid = self.db.get(uri)
        #logger.debug('db get %s: %s', uri, mbid)
        return mbid

    def _get_mbid_silent(self, uri):
        return self.db.get(uri)

    def add_mbid(self, uri, mbid):
        logger.debug('db add %s: %s', uri, mbid)
        self.db[uri] = mbid

    def del_uri(self, uri):
        logger.debug('db del %s', uri)
        if not self._get_mbid_silent(uri):
            logger.debug('uri is not in db')
            return
        # raises KeyError if no such key
        del self.db[uri]

    def _validate_mbid(self, uri, mbid):
        if self._get_mbid_silent(uri):
            # FIXME: check if it is same
            logger.warning('FAIL: _validate_mbid: %s uri is already on db', uri)
            return
        self.add_mbid(uri, mbid)

    def _validate_mbids(self, uri, mbids):
        if not mbids:
            logger.debug('no mbids')
            return False
        if len(mbids) == 1:
            logger.debug('only one mbid, so add it to db')
            mbid = mbids[0]
            self._validate_mbid(uri, mbid)
            return True
        else:
            logger.debug('multiple mbids, not adding any')
            return False

    def _remove_bad_data_from_db(self):
        # length mismatch
        self.del_uri('spotify:track:0FlNSJQaK8ntxwOHetrgQY')
        self.del_uri('spotify:track:5C8kdULh3GjB8sxSiIj2vJ')
        self.del_uri('spotify:artist:2tt3u8V6gNUHjzgLqwhmgP')
        self.del_uri('spotify:track:1d4pALmklLIG8xQhXsTNnf')

    def feed_track_id(self, track_id):
        self._search_with_search_modes(track_id)

    def _search_with_search_modes(self, track_id):
        if 'strict' in self.search_modes:
            self.strict_search = True
            self.fuzzy_search = False
            self._search(track_id)
        if 'fuzzy' in self.search_modes:
            self.strict_search = False
            self.fuzzy_search = True
            self._search(track_id)

    def _search(self, track_id):
        track = self.toukka.sp.track(track_id)
        album = self.toukka.sp.album(track.get('album').get('id'))
        logger.debug('strict_search %s, fuzzy_search %s', self.strict_search, self.fuzzy_search)

        # try this first
        if self.fuzzy_search:
            self._search_with_extract(track)

        try:
            self._search_track(track)
        except ValidationFailed as e:
            logger.debug('found something but failed validate')

        try:
            self._search_album(album)
        except ValidationFailed as e:
            logger.debug('found something but failed validate')

        artists = track.get('artists') + album.get('artists')
        self._search_artists(artists)

        # and try again last
        if self.fuzzy_search:
            self._search_with_extract(track)

    def _search_artists(self, artists):

        artists_ids = set()
        for artist in artists:
            artists_ids.add(artist.get('id'))

        for artist_id in artists_ids:
            artist = self.toukka.sp.artist(artist_id)
            try:
                self._search_artist(artist)
            except ValidationFailed as e:
                logger.debug('found someting but failed validate')

    def _search_with_extract(self, track):
        logger.debug('_search_with_extract')
        album = track.get('album')
        track_uri = track.get('uri')
        album_uri = album.get('uri')
        track_mbid = self._get_mbid_silent(track_uri)
        album_mbid = self._get_mbid_silent(album_uri)

        if len(track.get('artists')) != 1:
            logger.debug('warn: multiple artists, using first one')

        artist = track.get('artists')[0]
        artist_uri = artist.get('uri')
        artist_mbid = self._get_mbid_silent(artist_uri)

        logger.debug('track: %s, album: %s, artist: %s', track_mbid, album_mbid, artist_mbid)

        if track_mbid and not artist_mbid:
            logger.debug('track found, trying extract artist from it')
            try:
                self._extract_artists_from_recording(track, self._get_recording_by_track(track))
            except ValidationFailed as e:
                logger.debug('found someting but failed validate')

        if track_mbid and not album_mbid:
            logger.debug('track found, trying extract album from it')
            try:
                self._extract_album_from_recording(track, self._get_recording_by_track(track))
            except ValidationFailed as e:
                logger.debug('found someting but failed validate')

        if album_mbid and not artist_mbid:
            logger.debug('album found, trying extract artist from it')
            try:
                self._extract_artists_from_release(album, self._get_release_by_album(album))
            except ValidationFailed as e:
                logger.debug('found someting but failed validate')


    def _search_track(self, track):
        if self._get_mbid_silent(track.get('uri')):
            return

        if self.strict_search:
            self._search_track_by_url(track)
            self._search_track_by_isrc(track)

        if self.fuzzy_search:
            for artist in track.get('artists'):
                self._search_track_by_data(track, artist=artist, media_format='Digital Media')
                self._search_track_by_data(track, artist=artist, media_format='CD')
                # other than Digital Media or CD most likely is bad choice
                self._search_track_by_data(track, artist=artist)
                # this is even worse choice
                self._search_track_by_data(track, artist=artist, with_album_name=False)
                # outch
                self._search_track_by_data(track, artist=artist, with_track_name=False)

        return

    def _search_track_by_isrc(self, track):
        if self._get_mbid_silent(track.get('uri')):
            return

        isrc = self._fix_isrc(track.get('external_ids').get('isrc'))
        mbids = self._search_recording_by_isrc_from_musicbrainz(isrc)
        return self._found_track_mbids(track, mbids)

    def _search_track_by_url(self, track):
        if self._get_mbid_silent(track.get('uri')):
            return

        url = track.get('external_urls').get('spotify')
        mbids = self._search_recording_by_url_from_musicbrainz(url)
        return self._found_track_mbids(track, mbids)

    def _search_track_by_data(self, track,
                              artist=None,
                              with_artist=True,
                              with_album=True,
                              with_album_name=True,
                              with_track_name=True,
                              with_track_position=True,
                              with_release_status=True,
                              media_format=None):
        if self._get_mbid_silent(track.get('uri')):
            return

        logger.debug('_search_track_by_data, with_album_name %s, media_format %s',
                     with_album_name, media_format)

        fields = dict()

        if with_artist:
            # cos musicbrainzngs and musicbrainz search sucks
            if artist is None:
                logger.debug('warn: no artist given using first one')
                artist = track.get('artists')[0]

            artist_mbid = self._get_mbid_silent(artist.get('uri'))

            if artist_mbid:
                # artist id
                fields['arid'] = artist_mbid
            else:
                # artist name is name(s) as it appears on the recording
                fields['artist'] = artist.get('name')

        if with_album:
            album = track.get('album')
            # track.album object is simplified
            album = self.toukka.sp.album(album.get('id'))
            album_mbid = self._get_mbid_silent(album.get('uri'))

            if album_mbid:
                fields['reid'] = album_mbid
            else:
                if with_album_name:
                    fields['release'] = album.get('name')
                else:
                    logger.debug('not adding album name to fields')

                if media_format:
                    fields['format'] = media_format

                # number of tracks on release as a whole
                fields['tracksrelease'] = album.get('tracks').get('total')

        if with_track_name:
            # name of recording or a track associated with the recording
            # fields['recording'] = self._normalize_string(track.get('name'))

            # name of the recording with any accent characters retained
            fields['recordingaccent'] = track.get('name')

        if with_track_position:
            # track number on medium
            fields['tnum'] = track.get('track_number')
            # the medium that the recording should be found on, first medium is position 1
            fields['position'] = track.get('disc_number')

        if with_release_status:
            # Release status (official, promotion, Bootleg, Pseudo-Release)
            fields['status'] = 'official'

        mbids = self._search_recording_by_data_from_musicbrainz(**fields)
        self._found_track_mbids(track, mbids)

    def _found_track_mbids(self, track, mbids):
        if not mbids:
            return False
        elif len(mbids) != 1:
            logger.debug('fail: multiple mbids: %s', mbids)
            return False
        elif len(mbids) == 1:
            mbid = mbids[0]
            return self._found_track_mbid(track, mbid)

    def _found_track_mbid(self, track, mbid):
        if not mbid:
            logger.debug('no mbid')
            return False
        elif self._validate_track_mbid(track, mbid):
            uri = track.get('uri')
            return self._validate_mbid(uri, mbid)
        else:
            logger.debug('failed validate')
            return False

    def _validate_track_mbid(self, track, mbid):
        logger.debug('validating track (%s), mbid (%s)', track.get('uri'), mbid)

        recording = self.toukka.mb.get_recording(mbid)

        # spotify do not have videos
        if recording.get('video'):
            logger.debug('fail: recording is video, failing...')
            raise ValidationFailed()

        # recording legth may be None, failing cos length_difference bails with None
        if recording.get('length') is None:
            logger.debug('fail: recording length is None')
            return ValidationFailed()

        # check length difference, ms
        track_length = track.get('duration_ms')
        recording_length = recording.get('length')
        length_difference = abs(track_length-recording_length)
        logger.debug('track length: %i, recording length: %i, difference: %i',
                     track_length, recording_length, length_difference)
        if length_difference > 2000:   # 2s
            logger.debug('fail: length_difference < 2000')
            raise ValidationFailed()

        # artists matching
        track_artists = ', '.join([a.get('name') for a in track.get('artists')])
        recording_artists = self._musicbrainz_artist_credit_to_string(recording.get('artist-credit'))
        logger.debug('track_artists: %s', track_artists)
        logger.debug('recording_artists: %s', recording_artists)
        if not self._compare_strings(track_artists, recording_artists):
            logger.debug('fail: track_artists != recording_artists')
            raise ValidationFailed()

        # check validy
        is_isrc_ok = False
        is_name_ok = False
        is_ok = False

        track_isrc = self._fix_isrc(track.get('external_ids').get('isrc'))
        recording_isrcs = recording.get('isrcs')

        if len(recording_isrcs) == 0:
            logger.debug('warn: recording without ISRCs')
            is_isrc_ok = True
        elif len(recording_isrcs) == 1:
            if track_isrc in recording_isrcs:
                logger.debug('ok: track_isrc is in recording_isrcs')
                is_isrc_ok = True
            else:
                logger.debug('fail: track_isrc is not in recording_isrcs')
                is_isrc_ok = False
        elif len(recording_isrcs) > 1:
            logger.debug('warn: recording has multiple ISRCs: %s', recording.get('isrcs'))
            if track_isrc in recording_isrcs:
                logger.debug('ok: track_isrc is in recording_isrcs')
                is_isrc_ok = True
            else:
                logger.debug('fail: track_isrc is not in recording_isrcs')
                is_isrc_ok = False

        track_name = track.get('name')
        recording_name = recording.get('title')

        if self._compare_strings(track_name, recording_name):
            logger.debug('ok: track_name == recording_name')
            is_name_ok = True
        elif track_name.lower() in recording_name.lower():
            logger.debug('warn: track_name in recording_name')
            is_name_ok = True
        elif recording_name.lower() in track_name.lower():
            logger.debug('warn: recording_name in track_name')
            is_name_ok = True
        else:
            logger.debug('fail: track_name (%s) != recording_name (%s)', track_name, recording_name)
            is_name_ok = False

        if is_isrc_ok and is_name_ok:
            is_ok = True
        # FIXME: remove when name has fuzzy matching
        elif is_isrc_ok and not is_name_ok:
            logger.debug('isrc check is ok and name check failed, forcing ok')
            is_ok = True
        else:
            is_ok = False
            raise ValidationFailed()

        logger.debug('is_isrc_ok %s, is_name_ok %s, is_ok %s', is_isrc_ok, is_name_ok, is_ok)
        # add it to db
        return is_ok

    def _get_recording_by_track(self, track):
        logger.debug('_get_recording_by_track')
        return self.toukka.mb.get_recording(self.get_mbid(track.get('uri')))

    def _get_release_by_album(self, album):
        logger.debug('_get_recording_by_album')
        return self.toukka.mb.get_release(self.get_mbid(album.get('uri')))

    def _extract_artists_from_recording(self, track, recording):
        logger.debug('trying extract artists from recording')
        mbids = list()
        if len(track.get('artists')) != 1:
            logger.debug('multiple track artists, not implemented')
            return False
        if len(recording.get('artist-credit')) != 1:
            logger.debug('multiple recording artists, not implemented')
            return False

        track_artist = track.get('artists')[0]
        track_artist_name = track_artist.get('name')
        recording_artist = recording.get('artist-credit')[0].get('artist')
        recording_artist_name = recording_artist.get('name')
        if self._compare_strings(track_artist_name, recording_artist_name):
            logger.debug('track artist name and recording artist name matches, so we may found artist mbid')
            mbids.append(recording_artist.get('id'))
        else:
            logger.debug('track artist name and recording artist name mismatches, tan: %s, ran: %s', track_artist_name, recording_artist_name)

        return self._found_artist_mbids(track_artist, mbids)

    def _extract_artists_from_release(self, album, release):
        logger.debug('trying extract artists from release')
        mbids = list()
        if len(album.get('artists')) != 1:
            logger.debug('multiple album artists, not implemented')
            return False
        if len(release.get('artist-credit')) != 1:
            logger.debug('multiple release artists, not implemented')
            return False

        album_artist = album.get('artists')[0]
        album_artist_name = album_artist.get('name')
        release_artist = release.get('artist-credit')[0].get('artist')
        release_artist_name = release_artist.get('name')
        if self._compare_strings(album_artist_name, release_artist_name):
            logger.debug('album artist name and release artist name matches, so we may found artist mbid')
            mbids.append(release_artist.get('id'))
        else:
            logger.debug('album artist name and release artist name mismatches, tan: %s, ran: %s', album_artist_name, release_artist_name)

        return self._found_artist_mbids(album_artist, mbids)

    def _extract_album_from_recording(self, track, recording):
        logger.debug('trying extract album from recording')

        mbids = list()
        track_album = track.get('album')
        track_album_name = track_album.get('name')
        releases = recording.get('releases')
        if len(releases) > 1:
            logger.debug('warn: recording linked to %s releases', len(releases))

        for release in releases:
            release_name = release.get('title')
            if self._compare_strings(track_album_name, release_name):
                logger.debug('track album name and recording album name matches, so we may found release mbid')
                mbids.append(release.get('id'))
            else:
                logger.debug('track album name and recording album name mismatches')
                logger.debug('track_album_name: %s, release_name: %s', track_album_name, release_name)

        return self._found_album_mbids(track_album, mbids)

    def _found_artist_mbids(self, artist, mbids):
        if not mbids:
            return False
        if len(mbids) != 1:
            logger.debug('fail: multiple mbids: %s', mbids)
            return False
        elif len(mbids) == 1:
            mbid = mbids[0]
            return self._found_artist_mbid(artist, mbid)

    def _found_artist_mbid(self, artist, mbid):
        logger.debug('found artist (%s) mbid (%s)', artist.get('uri'), mbid)

        if not mbid:
            logger.debug('no mbid')
            return False
        elif self._validate_artist_mbid(artist, mbid):
            uri = artist.get('uri')
            return self._validate_mbid(uri, mbid)
        else:
            logger.debug('failed validate')
            return False

    def _validate_artist_mbid(self, artist, mbid):
        logger.debug('validating artist (%s) mbid (%s)', artist.get('uri'), mbid)

        is_ok = False

        sp_artist = artist
        mb_artist = self.toukka.mb.get_artist(mbid)

        sp_artist_name = sp_artist.get('name')
        mb_artist_name = mb_artist.get('name')

        if self._compare_strings(sp_artist_name, mb_artist_name):
            logger.debug('ok: sp_artist_name == mb_artist_name')
            is_ok = True
        else:
            logger.debug('fail: sp_artist_name (%s) != mb_artist_name (%s)', sp_artist_name, mb_artist_name)
            is_ok = False

            # FIXME: graaa
            mb_artist_aliases = mb_artist.get('aliases')
            mb_artist_aliases_filtered = list()
            for a in mb_artist_aliases:
                if (a.get('type') == 'Artist name' and a.get('primary') is True and a.get('locale') == 'en'):
                    mb_artist_aliases_filtered.append(a.get('name'))
            logger.debug('mb_artist_aliases_filtered: %s', mb_artist_aliases_filtered)
            if sp_artist_name in mb_artist_aliases_filtered:
                logger.debug('ok: sp_artist_name in mb_artist_aliases_filtered')
                is_ok = True
            else:
                logger.debug('fail: sp_artist_name not in mb_artist_aliases_filtered')
                is_ok = False

        return is_ok

    def _found_album_mbids(self, album, mbids):
        if not mbids:
            return False
        elif len(mbids) != 1:
            logger.debug('fail: multiple mbids: %s', mbids)
            return False
        elif len(mbids) == 1:
            mbid = mbids[0]
            return self._found_album_mbid(album, mbid)

    def _found_album_mbid(self, album, mbid):
        if not mbid:
            logger.debug('no mbid')
            return False
        elif self._validate_album_mbid(album, mbid):
            uri = album.get('uri')
            return self._validate_mbid(uri, mbid)
        else:
            logger.debug('failed validate')
            return False

    def _validate_album_mbid(self, album, mbid):
        logger.debug('validating album (%s) mbid (%s)', album.get('uri'), mbid)

        # album object may be simplified, so get full album object
        album = self.toukka.sp.album(album.get('id'))
        release = self.toukka.mb.get_release(mbid)

        is_name_ok = False
        is_upc_ok = False
        is_ok = False

        # FIXME: check release and album type
        album_type = album.get('album_type').lower()
        release_type = release.get('release-group').get('primary-type').lower()

        if album_type == release_type:
            logger.debug('ok: album_type == release_type')
        else:
            logger.debug('fail: album_type (%s) != release_type (%s)', album_type, release_type)
            logger.debug('fail: no point check more, failing...')
            return False

        # album artists vs release artists
        album_artists = ', '.join([a.get('name') for a in album.get('artists')])
        release_artists = self._musicbrainz_artist_credit_to_string(release.get('artist-credit'))
        logger.debug('album_artists: %s', album_artists)
        logger.debug('release_artists: %s', release_artists)
        if not self._compare_strings(album_artists, release_artists):
            logger.debug('fail: album_artists != release_artists')
            return False

        # album name vs release name
        #
        album_name = album.get('name')
        release_name = release.get('title')
        release_name_with_disambiguation = release_name + ' ' + release.get('disambiguation')

        if self._compare_strings(album_name, release_name):
            logger.debug('ok: album_name == release_name')
            is_name_ok = True
        elif self._compare_strings(album_name, release_name_with_disambiguation):
            logger.debug('ok: album_name == release_name_with_disambiguation')
            is_name_ok = True
        elif album_name in release_name:
            logger.debug('ok: album_name in release_name')
            is_name_ok = True
        else:
            logger.debug('fail: album_name (%s) != release_name (%s)', album_name, release_name)
            is_name_ok = False

        album_upc = album.get('external_ids').get('upc')
        release_barcode = release.get('barcode')

        #is_upc_ok = self._compare_barcodes(album_upc, release_barcode)

        if self._compare_barcodes(album_upc, release_barcode):
            is_upc_ok = True
        elif release_barcode is None:
            logger.debug('warn: release_barcode is None')
            is_upc_ok = True
        else:
            logger.debug('fail: album_upc (%s) != release_barcode (%s)', album_upc, release_barcode)
            is_upc_ok = False

        if is_name_ok and is_upc_ok:
            is_ok = True
        else:
            is_ok = False
            raise ValidationFailed()

        return is_ok

    def _search_album(self, album):
        uri = album.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        if self.strict_search:
            self._search_album_by_url(album)
            self._search_album_by_upc_all(album)
            #self._search_album_by_upc(album, media_format='Digital Media')
            #self._search_album_by_upc(album, media_format='CD')
        if self.fuzzy_search:
            pass

    def _search_album_by_upc_all(self, album):
        if self._get_mbid_silent(album.get('uri')):
            return

        logger.debug('searching album by upc all variants')

        media_formats = ['Digital Media', 'CD', None]
        barcodes = set()

        album_upc = album.get('external_ids').get('upc')
        barcodes.add(album_upc)

        if len(album_upc) == 12:
            barcodes.add(self._convert_barcode_upc12_to_ean13(album_upc))
        elif len(album_upc) == 13:
            # check if country code is 0
            if album_upc[0] == '0':
                barcodes.add(self._convert_barcode_ean13_to_upc12(album_upc))
        elif len(album_upc) == 14:
            logger.debug('warn: album_upc (%s) is unknown format', album_upc)
            if len(album_upc) == 14 and album_upc[0] == '0' and album_upc[1] == '0':
                barcodes.add(album_upc[1:])
                barcodes.add(album_upc[2:])
        else:
            logger.debug('warn: album_upc (%s) is unknown format', album_upc)

        logger.debug('media_formats: %s', media_formats)
        logger.debug('barcodes: %s', barcodes)

        for media_format in media_formats:
            for barcode in barcodes:
                self._search_album_by_upc(album, barcode=barcode, media_format=media_format)

        return

    def _search_album_by_upc(self, album, barcode=None, media_format=None):
        if self._get_mbid_silent(album.get('uri')):
            return

        if barcode is None:
            barcode = album.get('external_ids').get('upc')

        logger.debug('search album by upc: barcode %s, media_format %s', barcode, media_format)

        fields = dict()
        fields['barcode'] = barcode
        fields['status'] = 'official'
        if media_format:
            fields['format'] = media_format

        mbids = self._search_release_by_data_from_musicbrainz(**fields)
        return self._found_album_mbids(album, mbids)

    def _search_album_by_url(self, album):
        if self._get_mbid_silent(album.get('uri')):
            return

        url = album.get('external_urls').get('spotify')
        mbids = self._search_release_by_url_from_musicbrainz(url)
        return self._found_album_mbids(album, mbids)

    def _search_artist(self, artist):
        if self._get_mbid_silent(artist.get('uri')):
            return

        if self.strict_search:
            self._search_artist_by_url(artist)
        if self.fuzzy_search:
            self._search_artist_by_data(artist)

    def _search_artist_by_url(self, artist):
        if self._get_mbid_silent(artist.get('uri')):
            return

        url = artist.get('external_urls').get('spotify')
        mbids = self._search_artist_by_url_from_musicbrainz(url)
        return self._found_artist_mbids(artist, mbids)

    def _search_artist_by_data(self, artist):
        if self._get_mbid_silent(artist.get('uri')):
            return

        fields = dict()
        fields['artist'] = artist.get('name')

        mbids = self._search_artist_by_data_from_musicbrainz(**fields)
        # FIXME: do not enable
        #self._found_artist_mbids(artist, mbids)
        return False

    def _search_recording_by_isrc_from_musicbrainz(self, isrc):
        logger.debug('searching isrc %s from musicbrainz', isrc)
        result = self.toukka.mb.get_recordings_by_isrc(isrc)
        mbids = list()
        if result:
            logger.debug('found %s recordings with isrc %s', len(result.get('recordings')), isrc)
            for r in result.get('recordings'):
                mbids.append(r.get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _search_release_by_upc_from_musicbrainz(self, upc):
        logger.debug('searching release by upc %s from musicbrainz', upc)
        mbids = list()
        result = self.toukka.mb.search_releases_with_upc(upc)
        if result:
            logger.debug('found %s releases from musicbrainz', result.get('count'))
            for r in result.get('releases'):
                mbids.append(r.get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _search_artist_by_url_from_musicbrainz(self, url):
        logger.debug('searching artist by url %s from musicbrainz', url)
        result = self.toukka.mb.browse_urls(url)
        mbids = list()
        if result:
            #pprint.pprint(result)
            logger.debug('found %s relations from musicbrainz', len(result.get('relations')))
            for relation in result.get('relations'):
                mbids.append(relation.get('artist').get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _search_release_by_url_from_musicbrainz(self, url):
        logger.debug('searching release by url %s from musicbrainz', url)
        mbids = list()
        result = self.toukka.mb.browse_urls(url)
        if result:
            #pprint.pprint(result)
            logger.debug('found {} relations from musicbrainz'.format(len(result.get('relations'))))
            for relation in result.get('relations'):
                mbids.append(relation.get('release').get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _search_recording_by_url_from_musicbrainz(self, url):
        logger.debug('searching recording by url %s from musicbrainz', url)
        mbids = list()
        result = self.toukka.mb.browse_urls(url)
        if result:
            #pprint.pprint(result)
            logger.debug('found {} relations from musicbrainz'.format(len(result.get('relations'))))
            for relation in result.get('relations'):
                mbids.append(relation.get('recording').get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _search_recording_by_data_from_musicbrainz(self, **fields):
        logger.debug('searching recording by data from musicbrainz')
        logger.debug('search fields: %s', fields)
        mbids = list()
        result = self.toukka.mb.search_recordings(strict=True, **fields)
        if result:
            logger.debug('found %s recordings from musicbrainz', result.get('count'))
            for r in result.get('recordings'):
                mbids.append(r.get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _search_release_by_data_from_musicbrainz(self, **fields):
        logger.debug('searching release by data from musicbrainz')
        logger.debug('search fields: %s', fields)
        mbids = list()
        result = self.toukka.mb.search_releases(strict=True, **fields)
        if result:
            logger.debug('found %s releases from musicbrainz', result.get('count'))
            for r in result.get('releases'):
                mbids.append(r.get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _search_artist_by_data_from_musicbrainz(self, **fields):
        logger.debug('searching artist by data from musicbrainz')
        logger.debug('search fields: %s', fields)
        mbids = list()
        result = self.toukka.mb.search_artists(strict=True, **fields)
        if result:
            logger.debug('found %s artists from musicbrainz', result.get('count'))
            for r in result.get('artists'):
                mbids.append(r.get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _normalize_string(self, string):
        # https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
        return ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn'))

    def _fix_isrc(self, isrc):
        return isrc.upper().replace('-', '')

    def _musicbrainz_artist_credit_to_string(self, artist_credit):
        return ''.join(c.get('name') + c.get('joinphrase') for c in artist_credit)

    def _musicbrainz_artist_credit_to_string_without_joinphrase(self, artist_credit):
        return ', '.join([c.get('name') for c in recording.get('artist-credit')])

    def _compare_strings(self, s1, s2):
        logger.debug('comparing strings: "%s", "%s", fuzz: %i', s1, s2, fuzzywuzzy.fuzz.ratio(s1, s2))
        if type(s1) != type(s2):
            logger.debug('fail: strings are different python type: %s, %s', type(s1), type(s2))
            return False
        elif s1 == s2:
            logger.debug('ok: strings are same')
            return True
        elif s1.lower() == s2.lower():
            logger.debug('ok: strings lowercase are same')
            return True
        # TODO: keep unicode and use transliteration tables
        elif unidecode.unidecode(s1) == unidecode.unidecode(s2):
            logger.debug('ok: strings transliterated ascii are same')
            return True
        elif unidecode.unidecode(s1).lower() == unidecode.unidecode(s2).lower():
            logger.debug('ok: strings lowercase transliterated ascii and are same')
            return True
        elif fuzzywuzzy.fuzz.ratio(s1, s2) >= 95:
            logger.debug('ok: strings fuzz ratio is >= 95')
            return True
        else:
            logger.debug('fail: strings not same')
            return False
        # just for sure
        return False

    def _compare_barcodes(self, b1, b2):
        logger.debug('comparing barcodes: %s, %s', b1, b2)
        if type(b1) != type(b2):
            logger.debug('fail: barcodes are different python type: %s, %s', type(b1), type(b2))
            return False
        elif b1 == b2:
            logger.debug('ok: barcodes are same')
            return True
        elif self._convert_barcode_to_ean13(b1) == self._convert_barcode_to_ean13(b2):
            logger.debug('ok: barcodes converted to ean13 are same')
            return True
        elif len(b1) != len(b2):
            logger.debug('fail: barcodes are different length: %s, %s', len(b1), len(b2))
            return False
        else:
            logger.debug('fail: barcodes not same')
            return False
        # just for sure
        return False

    def _convert_barcode_to_ean13(self, barcode):
        if len(barcode) == 13:
            return barcode
        if len(barcode) == 12:
            return '0' + barcode
        else:
            raise Exception()

    def _convert_barcode_upc12_to_ean13(self, barcode):
        return self._convert_barcode_to_ean13(barcode)

    def _convert_barcode_ean13_to_upc12(self, barcode):
        if len(barcode) == 13 and barcode[0] == '0':
            return barcode[1:]
        else:
            raise Exception()



class ValidationFailed(Exception):
    pass

# END
