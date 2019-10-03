#

'''spotify user information'''

import argh

from toukka.hub import Toukka
from toukka.utils import json_dump


def user_info(user_id):
    ''' Get public profile information about a Spotify user.'''
    toukka = Toukka()
    return json_dump(toukka.sp.user(user_id))


#
COMMANDS = [user_info]
