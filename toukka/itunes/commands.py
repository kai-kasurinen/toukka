#

'''itunes commands'''

import pprint
import argh
import itunes
from toukka import Toukka

#


@argh.wrap_errors([itunes.base.NoResultsFoundException])
def lookup(id):
    lookup = itunes.lookup(id)
    pprint.pprint(lookup.json)


@argh.wrap_errors([itunes.base.NoResultsFoundException])
def lookup_upc(upc):
    lookup = itunes.lookup_upc(upc)
    pprint.pprint(lookup.json)


def search_album(query, country=None):
    search = itunes.search_album(query)
    pprint.pprint(search)

#

NAMESPACE = 'itunes'

NAMESPACE_KWARGS = {
    'title': 'itunes',
    'description': 'itunes, itunes, itunes',
    'help': 'help, help, help'
    }

COMMANDS = [lookup,
            lookup_upc,
            search_album]

# END
