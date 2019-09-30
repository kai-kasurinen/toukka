#

import sopiva.spotify_watcher.spotify_watcher
import sopiva.spotify_watcher.playerctl_manager


def watch_spotify():
    return sopiva.spotify_watcher.spotify_watcher.run()


def watch_all_players():
    manager = sopiva.spotify_watcher.playerctl_manager.PlayerCtlManager(watch_only=['spotify'])
    mainloop = sopiva.spotify_watcher.playerctl_manager.MainLoop()
    mainloop.run()


COMMANDS = [watch_spotify, watch_all_players]

NAMESPACE = 'spotify'
NAMESPACE_KWARGS = {
    'title': 'Spotify',
    'description': 'spotify, spotify, spotify',
    'help': 'help, help, help'
    }

# END
