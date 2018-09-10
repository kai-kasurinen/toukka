#

import logging
import re
import requests
import musicbrainzngs

from beanbag.v2 import BeanBagException
from .search import MusicBrainzSearch
from .ws2 import MusicBrainzWS2
from .exceptions import HTTPErrorFake

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)


class MusicBrainzNGS:
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
        self._session = session
        self._search = MusicBrainzSearch(session=self._session)
        self._ws2 = MusicBrainzWS2(session=self._session)

    def auth(self, user, password):
        raise NotImplementedError()

    def set_useragent(self, app, version, contact=None):
        if not app or not version:
            raise ValueError('app and version can not be empty')
        if contact is not None:
            _useragent = '%s/%s python-musicbrainzngs-emulator/0.0.0 ( %s )' % (app, version, contact)
        else:
            _useragent = '%s/%s python-musicbrainzngs-emulator/0.0.0' % (app, version)
        self._session.headers.update({'User-Agent': _useragent})
        logger.debug('set user-agent to %s', _useragent)

    def set_hostname(self, hostname):
        raise NotImplementedError()

    def set_rate_limit(self, limit_or_interval=1.0, new_requests=1):
        raise NotImplementedError()

    def set_parser(self, new_parser_fun=None):
        raise NotImplementedError()

    def set_format(self, fmt='xml'):
        if fmt == 'xml':
            raise NotImplementedError()
        elif fmt == 'json':
            pass
        else:
            raise ValueError('invalid format: %s', fmt)

    def get_area_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('area', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_artist_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('artist', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_instrument_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('instrument', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)


    def get_label_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('label', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_place_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('place', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_event_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('event', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_recording_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('recording', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_release_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('release', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_release_group_by_id(self, mbid, includes=[], release_status=[], release_type=[]):
        return self._get_entity_by_id('release-group', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_series_by_id(self, mbid, includes=[]):
        return self._get_entity_by_id('series', mbid,
                                      includes=includes,
                                      release_status=release_status,
                                      release_type=release_type)

    def get_work_by_id(self, mbid, includes=[]):
        return self._get_entity_by_id('work', mbid, includes=includes)

    def get_url_by_id(self, mbid, includes=[]):
        return self._get_entity_by_id('url', mbid, includes=includes)

    def search_annotations(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('annotation', query, fields, limit, offset, strict)
        return self._search.annotation(**params)

    def search_areas(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('area', query, fields, limit, offset, strict)
        return self._search.area(**params)

    def search_artists(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('artist', query, fields, limit, offset, strict)
        return self._search.artist(**params)

    def search_events(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('event', query, fields, limit, offset, strict)
        return self._search.event(**params)

    def search_instruments(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('instrument', query, fields, limit, offset, strict)
        return self._search.instrument(**params)

    def search_labels(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('label', query, fields, limit, offset, strict)
        return self._search.label(**params)

    def search_places(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('place', query, fields, limit, offset, strict)
        return self._search.place(**params)

    def search_recordings(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('recording', query, fields, limit, offset, strict)
        return self._search.recording(**params)

    def search_releases(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('release', query, fields, limit, offset, strict)
        return self._search.release(**params)

    def search_release_groups(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('release-group', query, fields, limit, offset, strict)
        return self._search.release_group(**params)

    def search_series(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('serie', query, fields, limit, offset, strict)
        return self._search.series(**params)

    # not part of musicbrainzngs
    def search_tracks(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('recording', query, fields, limit, offset, strict)
        return self._search.track(**params)

    def search_works(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('work', query, fields, limit, offset, strict)
        return self._search.work(**params)

    def get_releases_by_discid(self, mbid, includes=[], toc=None, cdstubs=True, media_format=None):
        raise NotImplementedError()

    def get_recordings_by_isrc(self, isrc, includes=[], release_status=[], release_type=[]):
        params = musicbrainzngs.musicbrainz._check_filter_and_make_params('isrc',
                                                                          includes,
                                                                          release_status,
                                                                          release_type)
        return self._do_mb_query('isrc', isrc, includes, params)

    def get_work_by_iswc(self, iswc, includes=[]):
        return self._do_mb_query('iswc', iswc, includes)

    def browse_artists(self, recording=None, release=None, release_group=None, work=None, includes=[], limit=None, offset=None):
        params = {
            "recording": recording,
            "release": release,
            "release-group": release_group,
            "work": work
            }
        return self._browse_impl('artist', includes, limit, offset, params)

    def browse_urls(self, resource=None, includes=[], limit=None, offset=None):
        params = {"resource": resource}
        return self._browse_impl("url", includes, limit, offset, params)

    # internals

    def _get_entity_by_id(self, entity_type, mbid, includes=[], release_status=[], release_type=[]):
        params = musicbrainzngs.musicbrainz._check_filter_and_make_params(entity_type,
                                                              includes,
                                                              release_status,
                                                              release_type)
        return self._do_mb_query(entity_type, mbid, includes, params)


    def _browse_impl(self, entity, includes, limit, offset, params, release_status=[], release_type=[]):
        includes = includes if isinstance(includes, list) else [includes]
        valid_includes = musicbrainzngs.musicbrainz.VALID_BROWSE_INCLUDES[entity]
        musicbrainzngs.musicbrainz._check_includes_impl(includes, valid_includes)
        p = {}
        for k,v in params.items():
            if v:
                p[k] = v
        if len(p) > 1:
            raise Exception("Can't have more than one of " + ", ".join(params.keys()))
        if limit: p["limit"] = limit
        if offset: p["offset"] = offset
        filterp = musicbrainzngs.musicbrainz._check_filter_and_make_params(entity, includes, release_status, release_type)
        p.update(filterp)
        return self._do_mb_query(entity, "", includes, p)

    def _do_mb_query(self, entity, mbid, includes=[], params={}):
        (args, auth_required) = self._do_mb_query_args(entity, mbid, includes=includes, params=params)
        # TODO: do something with auth_required
        if mbid == '':
            ret = self._browse_entity(entity, mbid, includes=args['inc'], params=params)
        else:
            ret = self._get_entity(entity, mbid, includes=args['inc'])
        return ret

    def _do_mb_query_args(self, entity, mbid, includes=[], params={}):
        if not isinstance(includes, list):
            includes = [includes]
        musicbrainzngs.musicbrainz._check_includes(entity, includes)
        auth_required = musicbrainzngs.musicbrainz._get_auth_type(entity, mbid, includes)
        args = dict(params)
        if len(includes) > 0:
            inc = " ".join(includes)
            args["inc"] = inc
        return (args, auth_required)

    def _get_entity(self, entity, mbid, includes=None):
        try:
            ret = self._ws2._GET_ENTITY(entity, mbid, includes=includes)
        except BeanBagException as error:
            if error.response.status_code in (400, 404, 411):
                cause = HTTPErrorFake(error.response, error.msg)
                raise musicbrainzngs.ResponseError(cause=cause)
            else:
                raise

        return ret

    def _browse_entity(self, entity, mbid, includes=None, params=None):
        try:
            ret = self._ws2._BROWSE_ENTITY(entity, includes=includes, filters=params)
        except BeanBagException as error:
            if error.response.status_code in (400, 404, 411):
                cause = HTTPErrorFake(error.response, error.msg)
                raise musicbrainzngs.ResponseError(cause=cause)
            else:
                raise

        return ret


    def _do_mb_search_params(self, entity, query='', fields={}, limit=None, offset=None, strict=False):
        query_parts = []
        if query:
            clean_query = musicbrainzngs.util._unicode(query)
            if fields:
                clean_query = re.sub(musicbrainzngs.LUCENE_SPECIAL, r'\\\1',
                                clean_query)
                if strict:
                    query_parts.append('"%s"' % clean_query)
                else:
                    query_parts.append(clean_query.lower())
            else:
                query_parts.append(clean_query)
        for key, value in fields.items():
            # Ensure this is a valid search field.
            if key not in musicbrainzngs.VALID_SEARCH_FIELDS[entity]:
                raise musicbrainzngs.InvalidSearchFieldError(
                    '%s is not a valid search field for %s' % (key, entity)
                )

            # Escape Lucene's special characters.
            value = musicbrainzngs.util._unicode(value)
            value = re.sub(musicbrainzngs.LUCENE_SPECIAL, r'\\\1', value)
            if value:
                if strict:
                    query_parts.append('%s:"%s"' % (key, value))
                else:
                    value = value.lower() # avoid AND / OR
                    query_parts.append('%s:(%s)' % (key, value))
        if strict:
            full_query = ' AND '.join(query_parts).strip()
        else:
            full_query = ' '.join(query_parts).strip()

        if not full_query:
            raise ValueError('at least one query term is required')

        # Additional parameters to the search.
        params = {'query': full_query}
        if limit:
            params['limit'] = str(limit)
        if offset:
            params['offset'] = str(offset)

        return params


# END
