#

from . import playlist_cleaner
from . import playlist_creator
from . import playlists

#

COMMANDS = [
    *playlist_cleaner.COMMANDS,
    *playlist_creator.COMMANDS,
    *playlists.COMMANDS
]

NAMESPACE = 'experimental'

NAMESPACE_KWARGS = {
    'title': 'Experimental',
    'description': 'Experimental, experimental, experimental',
    'help': 'help, help, help'
    }

# END
