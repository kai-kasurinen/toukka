#

'''spotify user information'''

from toukka.sopiva.spotify.util import get_spotify


def user_info(user_id: str):
    ''' get public profile information about a Spotify user.'''
    return get_spotify().user(user_id).pprint()


#
COMMANDS = [user_info]
