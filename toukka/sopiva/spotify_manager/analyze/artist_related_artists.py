#


import collections

from toukka.sopiva.spotify.util import get_spotify


def artist_related_artists_counter(artist_id, depth=1):
    spotify = get_spotify()
    related_artists_counter = collections.Counter()

    related_artists = spotify.artist_related_artists(artist_id)
    related_artists_ids = [artist.id for artist in related_artists]
    related_artists_counter.update(related_artists_ids)


# END
