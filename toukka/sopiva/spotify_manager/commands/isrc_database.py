#

import toukka.sopiva.spotify_manager.database.track_to_isrc


def track_to_isrc_update():
    toukka.sopiva.spotify_manager.database.track_to_isrc.track_to_isrc_update()


def get_listened_isrcs():
    toukka.sopiva.spotify_manager.database.track_to_isrc.get_listened_isrcs()


#

COMMANDS = [
    track_to_isrc_update,
    get_listened_isrcs
    ]

# END
