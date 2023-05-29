#


import click
import wikidataintegrator

from ..cli import root


@root.command()
def hello():
    print('Hello!')



@root.command
@click.argument('artist_name')
def artist_info(artist_name):

    query = '''
    SELECT ?item ?itemLabel ?description WHERE {
        ?item rdfs:label "%s"@en.
        ?item schema:description ?description.
        FILTER (lang(?description) = "en")
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    ''' % artist_name

    results = wikidataintegrator.wdi_core.WDItemEngine.execute_sparql_query(query)
    for result in results['results']['bindings']:
        item_label = result['itemLabel']['value']
        description = result['description']['value']
        print(f"Artist: {item_label}")
        print(f"Description: {description}")
        print()




# END
