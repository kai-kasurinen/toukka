#

from . import playlist_cleaner
from . import playlist_creator
from . import playlists
from . import isrc_database

#

COMMANDS = [
    *playlist_cleaner.COMMANDS,
    *playlist_creator.COMMANDS,
    *playlists.COMMANDS,
    *isrc_database.COMMANDS
]

NAMESPACE = 'spotify-manager'

NAMESPACE_KWARGS = {
    'title': 'Experimental',
    'description': 'Experimental, experimental, experimental',
    'help': 'help, help, help'
    }

# END
