#

import pprint
import argh

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer import first as printer


@argh.arg('type', choices=['artist', 'album', 'track', 'playlist'])
def search(type: str,
           query: str,
           limit: int = None):

    # NOTE: cos default is None, argh (or some else) set it as str
    if limit is not None:
        limit = int(limit)

    spotify = get_spotify()
    search = spotify.search(query=query,
                            types=[type],
                            market=None,
                            limit=50)
    paging = search[0]
    # NOTE: next() not compatible with search results
    for count, item in enumerate(spotify.iterate_items_from_paging(paging), start=1):
        printer.printer(item)

        if limit is not None and count >= limit:
            break

#


COMMANDS = [
    search
]

# END
