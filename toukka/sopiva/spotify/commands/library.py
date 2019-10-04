#

import argh

from toukka.sopiva.spotify.util import get_spotify


@argh.aliases('saved-albums')
def current_user_saved_albums():
    return get_spotify().current_user_albums().pprint()


@argh.aliases('saved-tracks')
def current_user_saved_tracks():
    return get_spotify().current_user_tracks().pprint()


#

COMMANDS = [
    current_user_saved_albums,
    current_user_saved_tracks,
]

# END
