#

import argh

from toukka.sopiva.spotify.util import get_spotify


_RANGES_DESCRIPTION = {
    'long_term':   'calculated from several years',
    'medium_term': 'approximately last 6 months',
    'short_term': 'approximately last 4 weeks'
}


@argh.aliases('top-tracks')
@argh.arg('--time-range', choices=['short', 'medium', 'long'])
def current_user_top_tracks(time_range='long'):
    toukka = Toukka()

    if time_range not in ('short', 'medium', 'long'):
        raise Exception()

    time_range = '{}_term'.format(time_range)

    print('{}: {}'.format(time_range, _RANGES_DESCRIPTION.get(time_range)))
    print()

    results = toukka.sp.current_user_top_tracks(time_range=time_range, limit=50)

    for i, item in enumerate(results['items']):
        artists_string = _get_string_from_artists(item['artists'])
        print('{pos:2} {name:40} {artists_string}'.
              format(**item, pos=i+1, artists_string=artists_string))


@argh.aliases('top-artists')
@argh.arg('--time-range', choices=['short', 'medium', 'long'])
def current_user_top_artists(time_range='long'):
    spotify = get_spotify()

    time_range = f'{time_range}_term'

    results = spotify.current_user_top_artists(time_range=time_range, limit=50)

    def list_to_string(s):
        return ', '.join(map(str, s))

    print(f'{time_range}: {_RANGES_DESCRIPTION.get(time_range)}')
    print()

    for i, item in enumerate(results.items, start=1):
        print(f'{i:2} {item.name:50} {list_to_string(item.genres)}')


#

COMMANDS = [
    current_user_top_tracks,
    current_user_top_artists
    ]

# END
