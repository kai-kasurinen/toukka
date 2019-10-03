#

import pprint
import argh
from .. import MusicBrainzWS2


def get_area(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.area(mbid))


def get_artist(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.artist(mbid))


def get_event(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.event(mbid))


def get_instrument(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.instrument(mbid))


def get_label(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.label(mbid))


def get_place(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.place(mbid))


def get_recording(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.recording(mbid))


def get_release(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.release(mbid))


def get_release_group(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.release_group(mbid))


def get_series(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.series(mbid))


def get_work(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.work(mbid))


def get_url(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.url(mbid))


def get_discid(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.discid(mbid))


def get_isrc(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.isrc(mbid))


def get_iswc(mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2.iswc(mbid))


def get_entity(entity_type, mbid):
    ws2 = MusicBrainzWS2()
    return pprint.pformat(ws2._GET_ENTITY(entity_type, mbid))


def browse_entity(entity_type, filters_string):
    ws2 = MusicBrainzWS2()
    filters = dict(f.split('=') for f in filters_string.split(','))
    return pprint.pformat(ws2._BROWSE_ENTITY(entity_type, filters=filters))


COMMANDS = [
    get_area,
    get_artist,
    get_event,
    get_instrument,
    get_label,
    get_place,
    get_recording,
    get_release,
    get_release_group,
    get_series,
    get_work,
    get_url,
    get_discid,
    get_isrc,
    get_iswc,
    get_entity,
    browse_entity
]

# END
