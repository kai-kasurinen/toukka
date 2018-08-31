#


from . import toukka
from . import fun
from . import url
from . import playing

COMMANDS = [
    *toukka.COMMANDS,
    *url.COMMANDS,
    *playing.COMMANDS,
    *fun.COMMANDS]

NAMESPACE = 'toukka'

NAMESPACE_KWARGS = {
    'title': 'Toukka',
    'description': 'toukka, toukka, toukka',
    'help': 'help, help, help'
    }

