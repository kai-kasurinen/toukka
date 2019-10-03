#

import argh

import sopiva.spotify.work
import sopiva.spotify.work.experimental

#


def testing():
    return sopiva.spotify.work.experimental.testing()


def print_track(track_id):
    return sopiva.spotify.work.experimental.print_track(track_id)


@argh.named('top-artists')
@argh.arg('--time-range', choices=['short', 'medium', 'long'])
def current_user_top_artists(time_range='long'):
    return sopiva.spotify.work.experimental.current_user_top_artists(time_range)


#

COMMANDS = [testing, print_track, current_user_top_artists]

NAMESPACE = 'spotify'
NAMESPACE_KWARGS = {
    'title': 'Spotify',
    'description': 'spotify, spotify, spotify',
    'help': 'help, help, help'
    }

# END
