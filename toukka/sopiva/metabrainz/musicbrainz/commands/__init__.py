#

from . import search
from . import entity

NAMESPACE = 'musicbrainz'

NAMESPACE_KWARGS = {
    'title': 'Musicbrainz with beanbag',
    'description': 'musicbrainz, musicbrainz, musicbrainz',
    'help': 'help, help, help'
    }

COMMANDS = [*search.COMMANDS,
            *entity.COMMANDS]

# END
