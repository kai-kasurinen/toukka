#

'''finna commands'''

import pprint
import argh
from toukka.hub import Toukka


NAMESPACE = 'finna'
NAMESPACE_KWARGS = {
    'title': 'finna',
    'description': 'skeleton, skeleton, skeleton',
    'help': 'help, help, help'
}


def record(rid):
    toukka = Toukka()
    return pprint.pformat(toukka.finna.record(rid))

def search(lookfor):
    toukka = Toukka()
    return pprint.pformat(toukka.finna.search(lookfor))

#

COMMANDS = [record, search]

# END
