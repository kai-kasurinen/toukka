#

from . import playlist_cleaner
from . import playlist_generator_commands
from . import playlists
from . import genres

#

COMMANDS = [
    *playlist_cleaner.COMMANDS,
    *playlist_generator_commands.COMMANDS,
    *playlists.COMMANDS,
    *genres.COMMANDS,
]

NAMESPACE = 'spotify-manager'

NAMESPACE_KWARGS = {
    'title': 'Experimental',
    'description': 'Experimental, experimental, experimental',
    'help': 'help, help, help'
    }

# END
