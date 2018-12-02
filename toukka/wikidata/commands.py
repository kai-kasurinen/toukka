#

'''wikidata commands'''

import pprint
import argh


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
    entity = toukka.hub.wikidata.get(entity_id, load=True)

    if dump:
        pprint.pprint(entity)
        pprint.pprint(entity.data)
    else:
        print_entity(entity)


#

COMMANDS = [entity]

# END
