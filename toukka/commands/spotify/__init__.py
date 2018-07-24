#


from . import album
from . import artist
from . import browse
from . import me
from . import player
from . import playlist
from . import search
from . import track

COMMANDS = [
    *album.COMMANDS,
    *artist.COMMANDS,
    *browse.COMMANDS,
    *me.COMMANDS,
    *player.COMMANDS,
    *playlist.COMMANDS,
    *search.COMMANDS,
    *track.COMMANDS]

NAMESPACE = 'spotify'

NAMESPACE_KWARGS = {
    'title': 'Spotify',
    'description': 'spotify, spotify, spotify',
    'help': 'help, help, help'
    }

