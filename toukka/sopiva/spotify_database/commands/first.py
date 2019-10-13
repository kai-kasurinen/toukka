#

import toukka.sopiva.spotify_database.track_to_isrc


def track_to_isrc_update():
    toukka.sopiva.spotify_database.track_to_isrc.update()


#

COMMANDS = [
    track_to_isrc_update,
    ]

# END
