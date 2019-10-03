#

import pprint

from sopiva.spotify.util import get_spotify
from sopiva.spotify import printer


def testing():
    spotify = get_spotify()


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


_RANGES_DESCRIPTION = {
    'long_term':   'calculated from several years',
    'medium_term': 'approximately last 6 months',
    'short_term': 'approximately last 4 weeks'
}


def current_user_top_artists(time_range: 'short, medium or long'):
    spotify = get_spotify()

    if time_range not in ('short', 'medium', 'long'):
        raise Exception()

    time_range = '{}_term'.format(time_range)

    print('{}: {}'.format(time_range, _RANGES_DESCRIPTION.get(time_range)))
    print()

    results = spotify.current_user_top_artists(time_range=time_range, limit=50)

    def unpack(s):
        return ', '.join(map(str, s))

    for i, item in enumerate(results.items, start=1):
        print(f'{i:2} {item.name:50} {unpack(item.genres)}')




# END
