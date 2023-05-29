#


import click
import pprint

from ..cli import root
from ..wikidata import Wikidata

@root.command
@click.argument('name')
def search_entity(name):

    wikidata = Wikidata()
    results = wikidata.sparql.search_entities_by_name(name)

    for result in results.bindings:
        print(result)


@root.command
@click.argument('spotify_id')
def search_spotify_artist(spotify_id):
    wikidata = Wikidata()
    results = wikidata.sparql.search_spotify_artist(spotify_id)
    
    for result in results.bindings:
        print(result)


@root.command
@click.argument('entity_id')
@click.option('--dump', is_flag=True)
def entity(entity_id, dump=False):
    wikidata = Wikidata()

    entity = wikidata.client.get(entity_id, load=True)

    if entity is None:
        return

    if dump:
        pprint.pprint(entity)
        pprint.pprint(entity.data)
    else:
        wikidata.print_entity(entity)



# END
