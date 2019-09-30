#

from . import client
from . import printer


def print_track(track_id):
    spotify = client.get_spotify_with_client_credentials()

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
