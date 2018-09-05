#

'''wikidata commands'''

import pprint
import argh
from toukka import Toukka

NAMESPACE = 'wikidata'
NAMESPACE_KWARGS = {
    'title': 'wikidata',
    'description': 'skeleton, skeleton, skeleton',
    'help': 'help, help, help'
}



def entity(entity_id):
    toukka = Toukka()
    entity = toukka.hub.wikidata.get(entity_id, load=True)
    return pprint.pformat(entity.data)

#

COMMANDS = [entity]

# END
