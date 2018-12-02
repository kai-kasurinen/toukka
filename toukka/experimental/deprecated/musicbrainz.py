#

import logging
import warnings
import re
import urllib.parse
import functools
import pprint
import musicbrainzngs

from toukka.metabrainz.musicbrainz.ngs import MusicBrainzNGS

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)


class MusicBrainz:
    def __init__(self, session=None):
        self.mbngs_emulated = MusicBrainzNGS(session=session)
        self.mbngs = self.mbngs_emulated

    @functools.lru_cache(maxsize=32)
    def search_artists(self, query='', limit=None, offset=None, strict=False, **fields):
        return self.mbngs.search_artists(query=query, limit=limit, offset=offset, strict=strict, **fields)

    @functools.lru_cache(maxsize=32)
    def search_recordings(self, query='', limit=None, offset=None, strict=False, **fields):
        return self.mbngs.search_recordings(query=query, limit=limit, offset=offset, strict=strict, **fields)

    @functools.lru_cache(maxsize=32)
    def search_tracks(self, query='', limit=None, offset=None, strict=False, **fields):
        return self.mbngs.search_tracks(query=query, limit=limit, offset=offset, strict=strict, **fields)

    @functools.lru_cache(maxsize=32)
    def search_releases(self, query='', limit=None, offset=None, strict=False, **fields):
        return self.mbngs.search_releases(query=query, limit=limit, offset=offset, strict=strict, **fields)

    @functools.lru_cache(maxsize=32)
    def search_releases_with_upc(self, upc):
        return self.search_releases(barcode=upc)

    @functools.lru_cache(maxsize=32)
    def get_recordings_by_isrc(self, isrc):
        includes = self._get_includes('isrc')
        try:
            result = self.mbngs.get_recordings_by_isrc(isrc, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logger.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        assert(result.get('isrc') == isrc)
        return result

    @functools.lru_cache(maxsize=32)
    def get_recording(self, mbid):
        logger.debug('get_recording %s', mbid)
        # artists, releases, discids, media, artist-credits, isrcs, annotation, aliases,
        # tags, user-tags, ratings, user-ratings,
        # area-rels, artist-rels, label-rels, place-rels, event-rels,
        # recording-rels, release-rels, release-group-rels, series-rels,
        # url-rels, work-rels, instrument-rels
        #includes = ['artists', 'aliases', 'artist-rels', 'tags', 'ratings', 'isrcs']
        includes = self._get_includes('recording')
        try:
            result = self.mbngs.get_recording_by_id(mbid, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logger.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    @functools.lru_cache(maxsize=32)
    def get_release(self, mbid):
        logger.debug('get_release %s', mbid)
        #includes = ['artist-credits', 'tags', 'annotation', 'media', 'labels']
        includes = self._get_includes('release')
        try:
            result = self.mbngs.get_release_by_id(mbid, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logger.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    @functools.lru_cache(maxsize=32)
    def get_release_group(self, mbid):
        logger.debug('get_release group %s', mbid)
        includes = self._get_includes('release-group')
        try:
            result = self.mbngs.get_release_group_by_id(mbid, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logger.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    @functools.lru_cache(maxsize=32)
    def get_artist(self, mbid):
        logger.debug('get_artist %s', mbid)
        includes = self._get_includes('artist')
        try:
            result = self.mbngs.get_artist_by_id(mbid, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logger.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    @functools.lru_cache(maxsize=32)
    def get_work(self, mbid):
        logger.debug('get_work %s', mbid)
        # artists, aliases, annotation, tags, user-tags, ratings, user-ratings,
        # area-rels, artist-rels, label-rels, place-rels, event-rels, recording-rels,
        # release-rels, release-group-rels, series-rels, url-rels, work-rels, instrument-rels
        #includes = []

        includes = self._get_includes('work')
        # BUG: 400 Bad request without this
        try:
            includes.remove('artists')
        except ValueError:
            pass

        try:
            result = self.mbngs.get_work_by_id(mbid, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logger.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    @functools.lru_cache(maxsize=32)
    def browse_urls(self, url):
        logger.debug('browse_urls %s', url)
        includes = self._get_includes('url')
        try:
            result = self.mbngs.browse_urls(resource=url, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logger.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    def get_artist_url_relations(self, mbid):
        artist = self.get_artist(mbid)
        relations = artist.get('relations')
        return self._filter_url_relations(relations)

    def get_recording_url_relations(self, mbid):
        recording = self.get_recording(mbid)
        relations = recording.get('relations')
        return self._filter_url_relations(relations)

    def get_artist_url_relations_by_type(self, mbid, rtype):
        return self._filter_url_relations_by_type(rtype, self.get_artist_url_relations(mbid))

    def get_recording_work_relations(self, mbid):
        return self._filter_work_relations(
            self.get_recording_relations_by_target_type(mbid, 'work'))

    def get_recording_relations_by_target_type(self, mbid, target_type):
        recording = self.get_recording(mbid)
        return self._filter_relations_by_target_type(recording.get('relations'), target_type)

    def get_release_url_relations(self, mbid):
        release = self.get_release(mbid)
        relations = release.get('relations')
        return self._filter_url_relations(relations)

    def get_release_url_relations_by_type(self, mbid, rtype):
        return self._filter_url_relations_by_type(rtype, self.get_release_url_relations(mbid))

    def get_release_group_url_relations(self, mbid):
        release = self.get_release_group(mbid)
        relations = release.get('relations')
        return self._filter_url_relations(relations)

    def get_release_group_url_relations_by_type(self, mbid, rtype):
        return self._filter_url_relations_by_type(rtype, self.get_release_group_url_relations(mbid))

    def _filter_relations_by_target_type(self, relations, target_type):
        return [r for r in relations if r.get('target-type') == target_type]

    def _filter_work_relations(self, relations):
        return [r.get('work').get('id') for r in relations]

    def _filter_url_relations(self, relations):
        return [{'type': r.get('type'),
                 'url': r.get('url').get('resource')}
                for r in relations if r.get('target-type') == 'url']

    def _filter_url_relations_by_type(self, rtype, relations):
        return [r.get('url') for r in relations if r.get('type') == rtype]

    def get_artist_by_url(self, url):
        mbid = self._find_mbid_from_string(url)
        if not mbid:
            return
        return self.get_artist(mbid)

    def get_release_by_url(self, url):
        mbid = self._find_mbid_from_string(url)
        if not mbid:
            return
        return self.get_release(mbid)

    def _get_includes(self, ent):
        i = musicbrainzngs.VALID_INCLUDES.get(ent)
        try:
            i.remove('user-tags')
            i.remove('user-ratings')
        except ValueError:
            pass
        return i

    # https://github.com/beetbox/beets/blob/master/beets/autotag/mb.py#L468
    def _find_mbid_from_string(self, string):
        """Search for a MusicBrainz ID in the given string and return it. If
        no ID can be found, return None.
        """
        # Find the first thing that looks like a UUID/MBID.
        match = re.search(u'[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}', string)
        if match:
            return match.group()
        else:
            logger.debug('No MBID found from string (%s)', string)
            return

    def get_entity_url(self, entity_type, mbid):
        BASE_URL = 'https://musicbrainz.org/'
        return urllib.parse.urljoin(BASE_URL, entity_type + '/' + mbid)



#



# END
