#

import logging
import warnings
import re
import urllib.parse
import musicbrainzngs

logger = logging.getLogger(__name__)

class MusicBrainz:
    def __init__(self):
        self.mbngs = musicbrainzngs
        self.mbngs.set_useragent('toukka', '0.0.0')
        warnings.filterwarnings('ignore', 'The json format is non-official and may change at any time')
        self.mbngs.set_format(fmt='json')

    def get_isrc(self, isrc):
        includes = self._get_includes('isrc')
        try:
            result = self.mbngs.get_recordings_by_isrc(isrc, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logging.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        assert(result.get('isrc') == isrc)
        return result

    def search_releases_with_upc(self, upc):
        try:
            result = self.mbngs.search_releases(barcode=upc)
        except musicbrainzngs.ResponseError as error:
            logging.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

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
            logging.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    def get_release(self, mbid):
        logger.debug('get_release %s', mbid)
        #includes = ['artist-credits', 'tags', 'annotation', 'media', 'labels']
        includes = self._get_includes('release')
        try:
            result = self.mbngs.get_release_by_id(mbid, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logging.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    def get_artist(self, mbid):
        logger.debug('get_artist %s', mbid)
        includes = ['tags', 'ratings', 'annotation', 'aliases']
        # FIXME: Bad request!!
        #includes = self._get_includes('artist')
        try:
            result = self.mbngs.get_artist_by_id(mbid, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logging.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result

    def browse_urls(self, url):
        #includes = []
        includes = self._get_includes('url')
        try:
            result = self.mbngs.browse_urls(resource=url, includes=includes)
        except musicbrainzngs.ResponseError as error:
            logging.debug('HTTP error %s', error.cause.code)
            if error.cause.code == 404:
                return None
            else:
                raise
        return result


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
            logging.debug('No MBID found from string (%s)', string)
            return

    def get_entity_url(self, entity_type, mbid):
        BASE_URL = 'https://musicbrainz.org/'
        return urllib.parse.urljoin(BASE_URL, entity_type + '/' + mbid)



#



# END
