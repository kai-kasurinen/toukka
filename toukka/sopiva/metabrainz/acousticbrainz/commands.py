#
# type: ignore

'''acousticbrainz module'''

import pprint
import argh
from toukka import Toukka

NAMESPACE = 'acousticbrainz'
NAMESPACE_KWARGS = {
    'title': 'acousticbrainz',
    'description': 'skeleton, skeleton, skeleton',
    'help': 'help, help, help'
}


def get_count(mbid):
    toukka = Toukka()
    return pprint.pformat(toukka.acousticbrainz.get_count(mbid))


def get_low_level(mbid, number=0):
    toukka = Toukka()
    return pprint.pformat(toukka.acousticbrainz.get_low_level(mbid))


def get_high_level(mbid, number=0):
    toukka = Toukka()
    return pprint.pformat(toukka.acousticbrainz.get_high_level(mbid, number=number))


COMMANDS = [get_count, get_low_level, get_high_level]

# END
