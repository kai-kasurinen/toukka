#

from . import search

NAMESPACE = 'musicbrainz'

NAMESPACE_KWARGS = {
    'title': 'Musicbrainz with beanbag',
    'description': 'musicbrainz, musicbrainz, musicbrainz',
    'help': 'help, help, help'
    }

COMMANDS = [*search.COMMANDS]

# END
