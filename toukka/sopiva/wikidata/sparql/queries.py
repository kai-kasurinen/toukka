#

import SPARQLWrapper


class WikidataSPARQL:
    
    def __init__(self):
        self.sparql = SPARQLWrapper.SPARQLWrapper2('https://query.wikidata.org/sparql')
        
    def query(self, query):
        self.sparql.setQuery(query)
        return self.sparql.query()
        

    def search_entities_by_name(self, name):

        query = '''
            SELECT ?item ?itemLabel ?description WHERE {
                ?item rdfs:label "%s"@en.
                ?item schema:description ?description.
                FILTER (lang(?description) = "en")
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
            ''' % name

        return self.query(query)
    
    def search_spotify_artist(self, spotify_id):

        query = '''
            SELECT DISTINCT ?item ?itemLabel WHERE {
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }
            {
                SELECT DISTINCT ?item WHERE {
                ?item p:P1902 ?statement0.
                ?statement0 (ps:P1902) "%s".
                }
                LIMIT 100
            }
            }
            ''' % spotify_id
        
        return self.query(query)


