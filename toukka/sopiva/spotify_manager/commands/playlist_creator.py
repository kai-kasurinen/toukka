#
#

import argh
import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history


def playlist_creator():
    '''create playlist'''

    spotify = get_spotify()
    spotify_history = get_spotify_history()


#

COMMANDS = [
    playlist_creator,
    ]

# END
