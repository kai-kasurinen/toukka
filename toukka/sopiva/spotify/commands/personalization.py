#

import click

from toukka.sopiva.spotify.util import get_spotify
from ..cli import cli_root


@cli_root.group()
def personalization():
    pass


_RANGES_DESCRIPTION = {
    'long_term':   'calculated from several years',
    'medium_term': 'approximately last 6 months',
    'short_term': 'approximately last 4 weeks'
}


@personalization.command('top-tracks')
@click.argument('time-range', type=click.Choice(['short', 'medium', 'long']))
def current_user_top_tracks(time_range):
    spotify = get_spotify()
    time_range = f'{time_range}_term'
    print(f'{time_range}: {_RANGES_DESCRIPTION.get(time_range)}')
    print()
    paging = spotify.current_user_top_tracks(time_range=time_range, limit=50)
    for i, item in enumerate(spotify.all_items(paging), start=1):
        artists = ', '.join(artist.name for artist in item.artists)
        print(f'{i:2} {item.name:50} {artists}')


@personalization.command('top-artists')
@click.argument('time-range', type=click.Choice(['short', 'medium', 'long']))
def current_user_top_artists(time_range):
    spotify = get_spotify()
    time_range = f'{time_range}_term'
    print(f'{time_range}: {_RANGES_DESCRIPTION.get(time_range)}')
    print()
    paging = spotify.current_user_top_artists(time_range=time_range, limit=50)
    for i, item in enumerate(spotify.all_items(paging), start=1):
        genres = ', '.join(item.genres)
        print(f'{i:2} {item.name:50} {genres}')



# END
