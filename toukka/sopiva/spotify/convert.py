#

import collections
import tekore._convert

from tekore._convert import (
    ConversionError,
    IdentifierType,
    to_uri,
    to_url,
    check_type,
    check_id
)


_ntuple_from_uri = collections.namedtuple('FromUri', ['type', 'id'])
_ntuple_from_url = collections.namedtuple('FromUrl', ['type', 'id'])


def from_uri(uri: str):
    return _ntuple_from_uri(*tekore._convert.from_uri(uri))


def from_url(url: str):
    return _ntuple_from_uri(*tekore._convert.from_url(url))


# END
