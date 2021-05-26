#

'''spotify artist commands'''

import operator

import click

from click_params import StringListParamType

from toukka.printer import printer
from toukka.sopiva.spotify.cli import cli_root
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.resource import SpotifyResource


@cli_root.group()
def artist():
    pass


@artist.command()
@click.argument('uri')
def info(uri):
    '''get artist info'''
    spotify = get_spotify()
    resource = SpotifyResource.from_any(uri)
    artist = spotify.artist(resource.id)
    printer(artist)


@artist.command()
@click.argument('uri')
@click.option('--market')
@click.option('--include-groups',
              type=StringListParamType(','),
              help='album,appears_on,compilation,single',
              default='album,single,compilation')
@click.option('--sort-by-keys', type=StringListParamType())
@click.option('--sort-reversed', is_flag=True)
def albums(
        uri,
        market: str = None,
        include_groups: list = None,
        sort_by_keys: list = None,
        sort_reversed: bool = False
        ):
    '''get artist albums'''
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    paging = spotify.artist_albums(uri_id, market=market, include_groups=include_groups)
    albums = spotify.all_items(paging)

    if sort_by_keys:
        albums = sorted(albums, key=operator.attrgetter(*sort_by_keys), reverse=sort_reversed)

    for album in albums:
        printer(album)


@artist.command()
@click.argument('uri')
@click.option('--market', default='from_token')
def top_tracks(uri,
               market='from_token'):
    '''get artist top tracks'''
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    for track in spotify.artist_top_tracks(uri_id, market=market):
        printer(track)


@artist.command()
@click.argument('uri')
def related_artists(uri):
    '''get artist related artists'''
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    for artist in spotify.artist_related_artists(uri_id):
        printer(artist)


# END
