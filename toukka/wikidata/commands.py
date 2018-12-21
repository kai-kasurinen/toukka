#

'''wikidata commands'''

import pprint
import argh
import urllib.error


from toukka import Toukka
from toukka.wikidata.printer import print_entity


NAMESPACE = 'wikidata'
NAMESPACE_KWARGS = {
    'title': 'wikidata',
    'description': 'skeleton, skeleton, skeleton',
    'help': 'help, help, help'
}



def entity(entity_id, dump=False):
    toukka = Toukka()
    # FIXME:
    try:
        # load=True is important
        entity = toukka.hub.wikidata.get(entity_id, load=True)
    except urllib.error.HTTPError as error:
        if error.getcode() == 404:
            print('not found')
            entity = None
        else:
            raise

    if entity is None:
        return

    if dump:
        pprint.pprint(entity)
        pprint.pprint(entity.data)
    else:
        print_entity(entity)


#

COMMANDS = [entity]

# END
