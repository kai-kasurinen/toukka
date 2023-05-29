#

from .sparql.queries import WikidataSPARQL
from .client import get_wikidata_client, print_entity


class Wikidata:
    def __init__(self):
        self.sparql = WikidataSPARQL()
        self.client = get_wikidata_client()

    # TODO: remove
    def print_entity(self, entity):
        print_entity(entity)

    # END


# END
