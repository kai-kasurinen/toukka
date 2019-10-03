#

'''listenbrainz module'''

import pprint
import argh

from .api import ListenBrainz

NAMESPACE = 'listenbrainz'
NAMESPACE_KWARGS = {
    'title': 'listenbrainz',
    'description': 'skeleton, skeleton, skeleton',
    'help': 'help, help, help'
}


def get_listens(username):
    listenbrainz = ListenBrainz()
    return pprint.pformat(listenbrainz.get_listens(username))

def get_latest_import(username):
    listenbrainz = ListenBrainz()
    return pprint.pformat(listenbrainz.get_latest_import(username))




COMMANDS = [get_listens, get_latest_import]

# END
