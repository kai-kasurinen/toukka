#

import pprint

from sopiva.spotify.util import get_spotify
from sopiva.spotify import printer


def print_track(track_id):
    spotify = get_spotify()

    track = spotify.track(track_id, market=None)
    album = spotify.album(track.album.id, market=None)

    artists = set()
    artists.update(_get_all_artist_ids_from_item(track))
    artists.update(_get_all_artist_ids_from_item(album))

    print()
    for artist_id in artists:
        artist = spotify.artist(artist_id)
        printer.print_artist(artist)
        print()

    printer.print_album(album)
    print()
    printer.print_track(track)
    print()


def _get_all_artist_ids_from_item(item):
    artists = set()
    for artist in item.artists:
        artists.add(artist.id)
    return artists



# END
