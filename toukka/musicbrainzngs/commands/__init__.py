#

'''Musicbrainz'''

from . import commands


NAMESPACE = 'musicbrainzngs'

NAMESPACE_KWARGS = {
    'title': 'Musicbrainz with python-musicbrainzngs',
    'description': 'musicbrainz, musicbrainz, musicbrainz',
    'help': 'help, help, help'
    }

COMMANDS = [*commands.COMMANDS]

# END
