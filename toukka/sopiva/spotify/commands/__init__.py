#


from . import album
from . import artist
from . import browse
from . import me
from . import personalization
from . import player
from . import playlist
from . import search
from . import track
from . import user
from . import entity

COMMANDS = [
    *album.COMMANDS,
    *artist.COMMANDS,
    *browse.COMMANDS,
    *me.COMMANDS,
    *personalization.COMMANDS,
    *player.COMMANDS,
    *playlist.COMMANDS,
    *search.COMMANDS,
    *track.COMMANDS,
    *user.COMMANDS,
    *entity.COMMANDS]

NAMESPACE = 'spotify'

NAMESPACE_KWARGS = {
    'title': 'Spotify',
    'description': 'spotify, spotify, spotify',
    'help': 'help, help, help'
    }

