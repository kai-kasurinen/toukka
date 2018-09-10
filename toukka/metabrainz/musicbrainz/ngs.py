#

import re

import musicbrainzngs

from . import MusicBrainzSearch

class MusicBrainzNGS:
    def __init__(self, session=None):
        self._search = MusicBrainzSearch(session=session)

    def search_artists(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('artist', query, fields, limit, offset, strict)
        return self._search.artist(**params)

    def search_recordings(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('recording', query, fields, limit, offset, strict)
        return self._search.recording(**params)

    def search_tracks(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('recording', query, fields, limit, offset, strict)
        return self._search.track(**params)

    def search_releases(self, query='', limit=None, offset=None, strict=False, **fields):
        params = self._do_mb_search_params('release', query, fields, limit, offset, strict)
        return self._search.release(**params)

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
