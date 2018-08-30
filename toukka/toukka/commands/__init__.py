#


from . import toukka
from . import fun
from . import url

COMMANDS = [
    *toukka.COMMANDS,
    *url.COMMANDS,
    *fun.COMMANDS]

NAMESPACE = 'toukka'

NAMESPACE_KWARGS = {
    'title': 'Toukka',
    'description': 'toukka, toukka, toukka',
    'help': 'help, help, help'
    }

