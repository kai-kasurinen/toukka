#

import toukka.sopiva.spotify_watcher.spotify_watcher
import toukka.sopiva.spotify_watcher.playerctl_manager


def watch_spotify():
    return toukka.sopiva.spotify_watcher.spotify_watcher.run()


def watch_all_players():
    manager = toukka.sopiva.spotify_watcher.playerctl_manager.PlayerCtlManager()
    mainloop = toukka.sopiva.spotify_watcher.playerctl_manager.MainLoop()
    mainloop.run()


COMMANDS = [watch_spotify, watch_all_players]

NAMESPACE = 'spotify_watcher'
NAMESPACE_KWARGS = {
    'title': 'Spotify',
    'description': 'spotify, spotify, spotify',
    'help': 'help, help, help'
    }

# END
