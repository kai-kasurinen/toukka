#

import pprint

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer import first as printer

def search(query: str):
    spotify = get_spotify()
    search = spotify.search(query=query, market=None)
    # GRR
    tracks_paging = search[0]
    #tracks_paging.pprint()
    # BUG: TypeError: __init__() got an unexpected keyword argument 'tracks'
    for track in spotify.iterate_items_from_paging(tracks_paging):
        printer.print_track(track)

#

COMMANDS = [search]

# END
