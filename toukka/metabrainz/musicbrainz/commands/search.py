#

import pprint
import argh
from .. import MusicBrainzSearch

def search_artist(query):
    search = MusicBrainzSearch()
    return pprint.pformat(search.artist(query))


COMMANDS = [search_artist]

# END
