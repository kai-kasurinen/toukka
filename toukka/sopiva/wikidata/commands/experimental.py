#


import click
import pprint

from ..cli import root
from ..sparql.queries import WikidataSPARQL

@root.command()
def hello():
    print('Hello!')



@root.command
@click.argument('name')
def search_entity(name):
    
    wikidata = WikidataSPARQL()

    results = wikidata.search_entities_by_name(name)
        
    for result in results.bindings:
        print(result)


@root.command
@click.argument('spotify_id')
def search_spotify_artist(spotify_id):
    
    wikidata = WikidataSPARQL()

    results = wikidata.search_spotify_artist(spotify_id)
    
    for result in results.bindings:
        print(result)




# END
