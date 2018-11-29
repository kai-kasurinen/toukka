#


from . import toukka
from . import fun
from . import url
from . import playing
from . import playing_watcher
from . import caching_test

COMMANDS = [
    *toukka.COMMANDS,
    *url.COMMANDS,
    *playing.COMMANDS,
    *playing_watcher.COMMANDS,
    *fun.COMMANDS,
    *caching_test.COMMANDS]

NAMESPACE = 'toukka'

NAMESPACE_KWARGS = {
    'title': 'Toukka',
    'description': 'toukka, toukka, toukka',
    'help': 'help, help, help'
    }

