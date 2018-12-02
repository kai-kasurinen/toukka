#


#from . import toukka
#from . import fun
#from . import url
from . import spotify_playing
from . import spotify_playing_watcher
from . import spotify_playlist_manager
from . import spotify_artist

COMMANDS = [
    *spotify_playing.COMMANDS,
    *spotify_playing_watcher.COMMANDS,
    *spotify_playlist_manager.COMMANDS,
    *spotify_artist.COMMANDS]

NAMESPACE = 'experimental'

NAMESPACE_KWARGS = {
    'title': 'Experimental',
    'description': 'Experimental, experimental, experimental',
    'help': 'help, help, help'
    }

