#

import pprint
import argh

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer import first as printer


@argh.arg('type', choices=['artist', 'album', 'track', 'playlist'])
def search(type: str,
           query: str):
    spotify = get_spotify()
    search = spotify.search(query=query,
                            types=[type],
                            market=None,
                            limit=50)
    paging = search[0]
    # NOTE: next() not compatible with search results
    for count, item in enumerate(spotify.iterate_items_from_paging(paging), start=1):
        printer.printer(item)

        # FIXME: break before next() so we do not hit bugs
        if count >= 50:
            break

#


COMMANDS = [
    search
]

# END
