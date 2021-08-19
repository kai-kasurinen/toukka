#

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.printer import printer


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
@click.option('--time-range', type=click.Choice(['short', 'medium', 'long']), default='long')
@click.option('--output-format', type=click.Choice(['default', 'long']), default='default')
def current_user_top_tracks(
        time_range,
        output_format
        ):

    spotify = get_spotify()
    time_range = f'{time_range}_term'
    paging = spotify.current_user_top_tracks(time_range=time_range, limit=50)
    tracks = spotify.all_items(paging)

    # NOTE: sometimes spotify returns 0 items
    if paging.total == 0:
        paging.pprint()
        return

    print(f'{time_range}: {_RANGES_DESCRIPTION.get(time_range)}')
    print()

    for i, item in enumerate(tracks, start=1):

        if output_format == 'long':
            printer(item)
        elif output_format == 'default':
            artists = ', '.join(artist.name for artist in item.artists)
            print(f'{i:2} {item.name:50} {artists}')
        else:
            raise Exception()


@personalization.command('top-artists')
@click.option('--time-range', type=click.Choice(['short', 'medium', 'long']), default='long')
@click.option('--output-format', type=click.Choice(['default', 'long']), default='default')
def current_user_top_artists(
        time_range,
        output_format
        ):

    spotify = get_spotify()
    time_range = f'{time_range}_term'

    paging = spotify.current_user_top_artists(time_range=time_range, limit=50)
    artists = spotify.all_items(paging)

    # NOTE: sometimes spotify returns 0 items
    if paging.total == 0:
        paging.pprint()
        return

    print(f'{time_range}: {_RANGES_DESCRIPTION.get(time_range)}')
    print()

    for i, item in enumerate(artists, start=1):

        if output_format == 'long':
            printer(item)
        elif output_format == 'default':
            genres = ', '.join(item.genres)
            print(f'{i:2} {item.name:50} {genres}')
        else:
            raise Exception()


# END
