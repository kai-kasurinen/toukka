#

import sopiva.spotify.experimental


#

def print_track(track_id):
    return sopiva.spotify.experimental.print_track(track_id)


COMMANDS = [print_track]

NAMESPACE = 'spotify'
NAMESPACE_KWARGS = {
    'title': 'Spotify',
    'description': 'spotify, spotify, spotify',
    'help': 'help, help, help'
    }

# END
