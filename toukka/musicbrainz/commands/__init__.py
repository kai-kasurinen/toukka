#

'''Musicbrainz'''

from . import commands


NAMESPACE = 'musicbrainz'

NAMESPACE_KWARGS = {
    'title': 'Musicbrainz',
    'description': 'musicbrainz, musicbrainz, musicbrainz',
    'help': 'help, help, help'
    }

COMMANDS = [*commands.COMMANDS]

# END
