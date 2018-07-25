#


from . import toukka
from . import fun

COMMANDS = [
    *toukka.COMMANDS,
    *fun.COMMANDS]

NAMESPACE = 'toukka'

NAMESPACE_KWARGS = {
    'title': 'Toukka',
    'description': 'toukka, toukka, toukka',
    'help': 'help, help, help'
    }

