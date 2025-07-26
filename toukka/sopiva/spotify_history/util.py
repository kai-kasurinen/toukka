#

import toukka.sopiva.spotify_history.database.client


def get_spotify_history():
    return toukka.sopiva.spotify_history.database.client.SpotifyHistory()


# END
