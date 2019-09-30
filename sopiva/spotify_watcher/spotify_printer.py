
from ..spotify import client
from ..spotify import printer

import spotipy


class SpotifyPrinter:
    def __init__(self):
        self.spotify = client.get_spotify_with_client_credentials()

    def print_all_from_track(self, track_uri):
        uri_type, uri_id = spotipy.convert.from_uri(track_uri)
        track_id = uri_id

        track = self.spotify.track(track_id, market=None)
        album = self.spotify.album(track.album.id, market=None)

        artists = set()
        artists.update(_get_all_artist_ids_from_item(track))
        artists.update(_get_all_artist_ids_from_item(album))

        print()
        for artist_id in artists:
            artist = self.spotify.artist(artist_id)
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
