#

from .playerctl_manager import PlayerCtlManager
from .spotify_saver import SpotifySaver
from .glib_mainloop import MainLoop

# FIXME: move
def watch_all_players():
    '''for debugging only'''
    manager = PlayerCtlManager()
    mainloop = MainLoop()
    mainloop.run()


def saver():
    '''saves spotify mpris metadata to database'''
    spotify_saver = SpotifySaver()
    mainloop = MainLoop()
    mainloop.run()
#


COMMANDS = [
    watch_all_players,
    saver
]

# END
