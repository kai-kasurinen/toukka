#

import sopiva.spotify.experimental


#


def testing():
    return sopiva.spotify.experimental.testing()


def print_track(track_id):
    return sopiva.spotify.experimental.print_track(track_id)


COMMANDS = [testing, print_track]

NAMESPACE = 'spotify'
NAMESPACE_KWARGS = {
    'title': 'Spotify',
    'description': 'spotify, spotify, spotify',
    'help': 'help, help, help'
    }

# END
