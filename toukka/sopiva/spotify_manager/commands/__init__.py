#

from . import playlist
from . import playlists

#

COMMANDS = [
    *playlist.COMMANDS,
    *playlists.COMMANDS
]

NAMESPACE = 'experimental'

NAMESPACE_KWARGS = {
    'title': 'Experimental',
    'description': 'Experimental, experimental, experimental',
    'help': 'help, help, help'
    }

# END
