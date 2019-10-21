#

import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer


def album(uri):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    album = spotify.album(uri_id)
    printer(album)

#


COMMANDS = [album]

# END
