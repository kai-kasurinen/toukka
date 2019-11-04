#

'''spotify artist commands'''

import click
import spotipy

from click_params import StringListParamType

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.group()
def artist():
    pass


@artist.command()
@click.argument('uri')
def info(uri):
    '''get artist info'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    artist = spotify.artist(uri_id)
    printer(artist)


@artist.command()
@click.argument('uri')
@click.option('--market')
@click.option('--include-groups',
              type=StringListParamType(','),
              help='album,appears_on,compilation,single',
              default='album,single,compilation')
def albums(uri,
           market: str = None,
           include_groups: list = None):
    '''get artist albums'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    paging = spotify.artist_albums(uri_id, market=market, include_groups=include_groups)
    for album in spotify.all_items_from_paging(paging):
        printer(album)


@artist.command()
@click.argument('uri')
@click.option('--country', default='from_token')
def top_tracks(uri,
               country='from_token'):
    '''get artist top tracks'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    for track in spotify.artist_top_tracks(uri_id, country=country):
        printer(track)


@artist.command()
@click.argument('uri')
def related_artists(uri):
    '''get artist related artists'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    for artist in spotify.artist_related_artists(uri_id):
        printer(artist)


# END
