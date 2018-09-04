#

import logging
import shelve
import pprint
import unicodedata

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

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

    def get_mbid(self, uri):
        mbid = self.db.get(uri)
        logger.debug('db get %s: %s', uri, mbid)
        return mbid

    def _get_mbid_silent(self, uri):
        return self.db.get(uri)

    def add_mbid(self, uri, mbid):
        logger.debug('db add %s: %s', uri, mbid)
        self.db[uri] = mbid

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

    def feed_track_id(self, track_id):
        self._search(track_id)

    def _search(self, track_id):
        track = self.toukka.sp.track(track_id)
        album = self.toukka.sp.album(track.get('album').get('id'))

        self._search_track(track)
        self._search_album(album)

        for artist in track.get('artists'):
            self._search_artist(artist)

        for artist in album.get('artists'):
            self._search_artist(artist)

        self._pingpong(track, album)

    def _pingpong(self, track, album):
        track_uri = track.get('uri')
        album_uri = album.get('uri')
        track_mbid = self._get_mbid_silent(track_uri)
        album_mbid = self._get_mbid_silent(album_uri)

        if len(track.get('artists')) != 1:
            logger.debug('pingpong not support multiple artists')

        artist = track.get('artists')[0]
        artist_uri = artist.get('uri')
        artist_mbid = self._get_mbid_silent(artist_uri)

        logger.debug('pingpong, track: %s, album: %s, artist: %s', track_mbid, album_mbid, artist_mbid)

        if (track_mbid and album_mbid and artist_mbid):
            logger.debug('Yippii! track, album and artist found')
        elif (track_mbid and album_mbid and not artist_mbid):
            logger.debug('track and album found, artist still missing')
            self._extract_artists_from_recording(track, self._get_recording_by_track(track))
        elif (track_mbid and not album_mbid and artist_mbid):
            logger.debug('track and artist found, album still missing')
            self._extract_album_from_recording(track, self._get_recording_by_track(track))
        elif (track_mbid and not album_mbid and not artist_mbid):
            logger.debug('track found, album and artist still missing')
            self._extract_artists_from_recording(track, self._get_recording_by_track(track))
            self._extract_album_from_recording(track, self._get_recording_by_track(track))
        else:
            logger.debug('what is this?')


    def _search_track(self, track):
        uri = track.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        self._search_track_by_isrc(track)
        self._search_track_by_url(track)
        self._search_track_by_data(track)
        self._search_track_by_data(track, with_album_name=False)

    def _search_track_by_isrc(self, track):
        uri = track.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        isrc = self._fix_isrc(track.get('external_ids').get('isrc'))
        mbids = self._search_recording_isrc_from_musicbrainz(isrc)
        self._found_track_mbids(track, mbids)

    def _search_track_by_url(self, track):
        uri = track.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        url = track.get('external_urls').get('spotify')
        mbids = self._search_track_url_from_musicbrainz(url)
        self._found_track_mbids(track, mbids)

    def _search_track_by_data(self, track, with_album_name=True):
        uri = track.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        logger.debug('searching track by data from MusicBrainz')

        fields = dict()

        if len(track.get('artists')) == 1:
            artist = track.get('artists')[0]
            artist_mbid = self._get_mbid_silent(artist.get('uri'))
            if artist_mbid:
                # artist id
                fields['arid'] = artist_mbid
            else:
                # artist name is name(s) as it appears on the recording
                fields['artist'] = artist.get('name')
        else:
            logger.debug('multiple artists, dont know what to do')
            return

        album = track.get('album')
        album_mbid = self._get_mbid_silent(album.get('uri'))

        if album_mbid:
            fields['reid'] = album_mbid
        else:
            if with_album_name:
                fields['release'] = album.get('name')
            else:
                logger.debug('not adding album name to fields')

        # name of recording or a track associated with the recording
        #fields['recording'] = track.get('name')
        # name of the recording with any accent characters retained
        fields['recordingaccent'] = self._normalize_string(track.get('name'))
        # track number on medium
        fields['tnum'] = track.get('track_number')
        # the medium that the recording should be found on, first medium is position 1 
        fields['position'] = track.get('disc_number')

        mbids = list()
        logger.debug('search fields: %s', fields)
        result = self.toukka.mbngs.search_recordings(strict=True, **fields)
        if result:
            logger.debug('found %s recordings from MusicBrainz', result.get('count'))
            if result.get('count') == 0:
                return
            if result.get('count') == 1:
                logger.debug('only one found, so adding it')
                for r in result.get('recordings'):
                    mbids.append(r.get('id'))
            else:
                logger.debug('multiple found, dont know what to do')

            #pprint.pprint(result)
        else:
            logger.debug('failed, no result')

        self._found_track_mbids(track, mbids)

    def _found_track_mbids(self, track, mbids):
        if not mbids:
            return False
        if len(mbids) != 1:
            logger.debug('fail: multiple mbids: %s', mbids)
            return False
        elif len(mbids) == 1:
            mbid = mbids[0]
            self._found_track_mbid(track, mbid)

    def _found_track_mbid(self, track, mbid):
        if not mbid:
            logger.debug('no mbid')
            return False
        if self._validate_track_mbid(track, mbid):
            uri = track.get('uri')
            self._validate_mbid(uri, mbid)
            # FIXME
            # disabled, pingpong should do this
            #self._extract_recording_and_track(track, self._get_recording_by_track(track))
        else:
            logger.debug('failed validate')

    def _validate_track_mbid(self, track, mbid):
        logger.debug('validating track (%s) mbid (%s)', track.get('uri'), mbid)
        uri = track.get('uri')

        recording = self.toukka.mb.get_recording(mbid)

        if recording.get('video'):
            logger.debug('fail: recording is video, failing...')
            return False

        #pprint.pprint(recording)
        # check validy
        is_isrc_ok = False
        is_name_ok = False
        is_ok = False

        track_isrc = self._fix_isrc(track.get('external_ids').get('isrc'))
        recording_isrcs = recording.get('isrcs')

        if len(recording_isrcs) == 0:
            logger.debug('warning: recording without ISRCs')
            is_isrc_ok = True
        elif len(recording_isrcs) == 1:
            if track_isrc in recording_isrcs:
                logger.debug('ok: track_isrc is in recording_isrcs')
                is_isrc_ok = True
            else:
                logger.debug('fail: track_isrc is not in recording_isrcs')
                is_isrc_ok = False
        elif len(recording_isrcs) > 1:
            logger.debug('warning: recording has multiple ISRCs: %s', recording.get('isrcs'))
            if track_isrc in recording_isrcs:
                logger.debug('ok: track_isrc is in recording_isrcs')
                is_isrc_ok = True
            else:
                logger.debug('fail: track_isrc is not in recording_isrcs')
                is_isrc_ok = False

        track_name = track.get('name').lower()
        recording_name = recording.get('title').lower()

        if track_name == recording_name:
            logger.debug('ok: track_name == recording_name')
            is_name_ok = True
        elif track_name in recording_name:
            logger.debug('ok: track_name in recording_name')
            is_name_ok = True
        elif recording_name in track_name:
            logger.debug('ok: recording_name in track_name')
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

        logger.debug('is_isrc_ok %s, is_name_ok %s, is_ok %s', is_isrc_ok, is_name_ok, is_ok)
        # add it to db
        return is_ok

    def _get_recording_by_track(self, track):
        return self.toukka.mb.get_recording(self.get_mbid(track.get('uri')))

    def _extract_recording_and_track(self, track, recording):
        logger.debug('WARNING: trying extract artist and album from recording')
        self._extract_artists_from_recording(track, recording)
        self._extract_album_from_recording(track, recording)

    def _extract_artists_from_recording(self, track, recording):
        logger.debug('trying extract artists from recording')
        # try get artist
        if len(track.get('artists')) == 1 and len(recording.get('artist-credit')) == 1:
            logger.debug('track and recording has only one artist, check it')
            ta = track.get('artists')[0]
            ra = recording.get('artist-credit')[0].get('artist')
            tan = ta.get('name')
            ran = ra.get('name')
            if tan == ran:
                logger.debug('track artist name and recording artist name matches, so we found artist mbid')
                self._found_artist_mbid(ta, ra.get('id'))
            elif self._normalize_string(tan) == self._normalize_string(ran):
                logger.debug('track artist normalized name and recording artist normalized name matches, so we found artist mbid')
                pprint.pprint(ra)
                self._found_artist_mbid(ta, ra.get('id'))
            else:
                logger.debug('track artist name and recording artist name mismatches, tan: %s, ran: %s', tan, ran)
                logger.debug('WARNING: trying it anyway')
                self._found_artist_mbid(ta, ra.get('id'))
        else:
            logger.debug('multiple artists, not implemented')

    def _extract_album_from_recording(self, track, recording):
        logger.debug('trying extract album from recording')
        # try get album
        if len(recording.get('releases')) == 1:
            logger.debug('recording has only one release, check it')
            ta = track.get('album')
            ra = recording.get('releases')[0]
            # FIXME: need fuzzy
            tan = ta.get('name').lower().replace('-', '').replace('  ', ' ')
            ran = ra.get('title').lower().replace(':', '').replace('  ', ' ')
            if tan == ran:
                logger.debug('track album name and recording album name matches, so we may found release mbid')
                self._found_album_mbid(ta, ra.get('id'))
            elif self._normalize_string(tan) == self._normalize_string(ran):
                logger.debug('track album normalized name and recording album normalized name matches, so we may found release mbid')
                self._found_album_mbid(ta, ra.get('id'))
            elif tan in ran:
                logger.debug('track album name in recording album name, so we may found release mbid')
                self._found_album_mbid(ta, ra.get('id'))
            elif ran in tan:
                logger.debug('recording album name in track album name, so we may found release mbid')
                self._found_album_mbid(ta, ra.get('id'))
            else:
                logger.debug('track album name and recording album name mismatches, tan: %s, ran: %s', tan, ran)
        else:
            logger.debug('multiple releases, not implemented')


    def _found_artist_mbids(self, artist, mbids):
        if not mbids:
            return False
        if len(mbids) != 1:
            logger.debug('fail: multiple mbids: %s', mbids)
            return False
        elif len(mbids) == 1:
            mbid = mbids[0]
            self._found_artist_mbid(artist, mbid)

    def _found_artist_mbid(self, artist, mbid):
        logger.debug('found artist (%s) mbid (%s)', artist.get('uri'), mbid)

        if not mbid:
            logger.debug('no mbid')
            return False
        if self._validate_artist_mbid(artist, mbid):
            uri = artist.get('uri')
            self._validate_mbid(uri, mbid)
        else:
            logger.debug('failed validate')

    def _validate_artist_mbid(self, artist, mbid):
        logger.debug('validating artist (%s) mbid (%s)', artist.get('uri'), mbid)

        is_ok = False

        sp_artist = artist
        mb_artist = self.toukka.mb.get_artist(mbid)

        sp_artist_name = sp_artist.get('name')
        mb_artist_name = mb_artist.get('name')

        if sp_artist_name == mb_artist_name:
            logger.debug('ok: sp_artist_name == mb_artist_name')
            is_oḱ = True
        elif self._normalize_string(sp_artist_name) == self._normalize_string(mb_artist_name):
            logger.debug('ok: sp_artist_name_normalized == mb_artist_name_normalized')
            is_ok = True
        else:
            logger.debug('fail: sp_artist_name (%s) != mb_artist_name (%s)', sp_artist_name, mb_artist_name)
            is_ok = False

            # FIXME: gludge
            mb_artist_aliases = mb_artist.get('aliases')
            mb_artist_aliases_filtered = list()
            for alias in mb_artist_aliases:
                if (alias.get('type') == 'Artist name' 
                    and alias.get('primary') is True
                    and alias.get('locale') == 'en'):
                        mb_artist_aliases_filtered.append(alias.get('name'))

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
        if len(mbids) != 1:
            logger.debug('fail: multiple mbids: %s', mbids)
            return False
        elif len(mbids) == 1:
            mbid = mbids[0]
            self._found_album_mbid(album, mbid)

    def _found_album_mbid(self, album, mbid):
        if not mbid:
            logger.debug('no mbid')
            return False

        if self._validate_album_mbid(album, mbid):
            uri = album.get('uri')
            self._validate_mbid(uri, mbid)
        else:
            logger.debug('failed validate')


    def _validate_album_mbid(self, album, mbid):
        logger.debug('validating album (%s) mbid (%s)', album.get('uri'), mbid)

        release = self.toukka.mb.get_release(mbid)
        # album object may be simplified, so get full album object
        album = self.toukka.sp.album(album.get('id'))

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

        # FIXME: need fuzzy
        album_name = album.get('name').lower().replace('-', '').replace('  ', ' ')
        release_name = release.get('title').lower().replace(':', '').replace('  ', ' ')
        release_name_with_disambiguation = release_name + ' ' + release.get('disambiguation')

        if album_name == release_name:
            logger.debug('ok: album_name == release_name')
            is_name_ok = True
        elif album_name == release_name_with_disambiguation:
            logger.debug('ok: album_name == release_name_with_disambiguation')
            is_name_ok = True
        else:
            logger.debug('fail: album_name (%s) != release_name (%s)', album_name, release_name)
            is_name_ok = False

        album_upc = album.get('external_ids').get('upc')
        release_barcode = release.get('barcode')

        if release_barcode == None:
            logger.debug('ok: release_barcode is None')
            is_upc_ok = True
        elif album_upc == release_barcode:
            logger.debug('ok: album_upc == release_barcode')
            is_upc_ok = True
        else:
            logger.debug('fail: album_upc (%s) != release_barcode (%s)', album_upc, release_barcode)
            is_upc_ok = False

        if is_name_ok and is_upc_ok:
            is_ok = True
        else:
            is_ok = False

        return is_ok


    def _search_album(self, album):
        uri = album.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        self._search_album_by_upc(album)
        self._search_album_by_url(album)

    def _search_album_by_upc(self, album):
        uri = album.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        upc = album.get('external_ids').get('upc')
        mbids = self._search_album_upc_from_musicbrainz(upc)
        self._found_album_mbids(album, mbids)

    def _search_album_by_url(self, album):
        uri = album.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        url = album.get('external_urls').get('spotify')
        mbids = self._search_album_url_from_musicbrainz(url)
        self._found_album_mbids(album, mbids)

    def _search_artist(self, artist):
        uri = artist.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        self._search_artist_by_url(artist)
        #self._search_artist_by_data(artist)

    def _search_artist_by_url(self, artist):
        uri = artist.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        url = artist.get('external_urls').get('spotify')
        mbids = self._search_artist_url_from_musicbrainz(url)
        self._found_artist_mbids(artist, mbids)

    def _search_artist_by_data(self, artist):
        uri = artist.get('uri')

        if self._get_mbid_silent(uri):
            #logger.debug('%s uri is already on db', uri)
            return

        logger.debug('searching artist by data from musicbrainz')

        fields = dict()

        fields['artist'] = artist.get('name')

        mbids = list()
        logger.debug('search fields: %s', fields)
        result = self.toukka.mbngs.search_artists(strict=True, **fields)
        if result:
            logger.debug('found %s artists from musicbrainz', result.get('count'))
            #pprint.pprint(result)
        else:
            logger.debug('failed, no result')

        if result and result.get('count') == 1:
            logger.debug('only one found')
            for r in result.get('artists'):
                mbids.append(r.get('id'))
        else:
            pass

        return


    def _search_recording_isrc_from_musicbrainz(self, isrc):
        logger.debug('searching isrc %s from musicbrainz', isrc)
        result = self.toukka.mb.get_isrc(isrc)
        mbids = list()
        if result:
            #pprint.pprint(result)
            logger.debug('found %s recordings with isrc %s', len(result.get('recordings')), isrc)
            for r in result.get('recordings'):
                mbids.append(r.get('id'))
        else:
            logger.debug('failed, no result')
        return mbids


    def _search_album_upc_from_musicbrainz(self, upc):
        logger.debug('searching UPC %s from musicbrainz', upc)
        mbids = list()
        result = self.toukka.mb.search_releases_with_upc(upc)
        if result:
            logger.debug('found %s releases from musicbrainz', result.get('count'))
            for r in result.get('releases'):
                mbids.append(r.get('id'))
        else:
            logger.debug('failed, no result')
        return mbids

    def _search_artist_url_from_musicbrainz(self, url):
        logger.debug('searching artist url %s from musicbrainz', url)
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

    def _search_album_url_from_musicbrainz(self, url):
        logger.debug('searching album url %s from musicbrainz', url)
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

    def _search_track_url_from_musicbrainz(self, url):
        logger.debug('searching track url %s from musicbrainz', url)
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

    def _normalize_string(self, string):
        # https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
        return ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn'))

    def _fix_isrc(self, isrc):
        return isrc.upper().replace('-', '')




# END
