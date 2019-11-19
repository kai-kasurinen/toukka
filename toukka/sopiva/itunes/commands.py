#
# type: ignore

'''itunes commands'''

import pprint
import argh

import toukka.sopiva.itunes.lookup_countries

from toukka.hub import Toukka
from toukka.sopiva.itunes.itunes import iTunes


#

def lookup(**kwargs):
    pprint.pprint(kwargs)
    itunes = iTunes()
    lookup = itunes.lookup(**kwargs)
    pprint.pprint(lookup)


def lookup_upc(upc, country=None):
    itunes = iTunes()
    lookup = itunes.lookup(upc=upc, country=country)
    pprint.pprint(lookup)


def lookup_id(id, country=None, entity=None):
    itunes = iTunes()
    lookup = itunes.lookup(id=id, country=country, entity=entity)
    pprint.pprint(lookup)


def search_album(query, country=None):
    search = itunes.search_album(query)
    pprint.pprint(search)


def lookup_id_from_all_countries(id):
    toukka.itunes.lookup_countries.lookup_id_from_all_countries(id)



#

NAMESPACE = 'itunes'

NAMESPACE_KWARGS = {
    'title': 'itunes',
    'description': 'itunes, itunes, itunes',
    'help': 'help, help, help'
    }

COMMANDS = [lookup,
            lookup_upc,
            lookup_id,
            lookup_id_from_all_countries,
            search_album]

# END
