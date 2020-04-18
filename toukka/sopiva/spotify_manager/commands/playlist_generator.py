#
#

from typing import Dict, Union, List

import logging
import re

import click
import click_params

from click_params import StringListParamType

import tekore.convert
import tekore.client.api.browse

import toukka.sopiva.spotify_manager.genres

from toukka.sopiva.spotify_manager.playlist_generator import PlaylistGenerator
from toukka.sopiva.spotify_manager.cli import cli_root
from toukka.sopiva.spotify_manager.experimental.new_releases import search_new_releases


logger = logging.getLogger(__name__)


# TODO: add genetator options group and remove cxt.obj usage
# TODO: https://github.com/pallets/click/issues/108

@cli_root.group()
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--progress-bar/--no-progress-bar', default=False)
@click.option('--randomize', is_flag=True, default=False)
@click.option('--expand-track-to-album', is_flag=True)
@click.option('--expand-track-to-artists', is_flag=True)
@click.option('--expand-track-to-recommendations', is_flag=True)
@click.option('--expand-artist-to-albums', is_flag=True)
@click.option('--expand-artist-to-random-album', is_flag=True)
@click.option('--expand-artist-to-top-tracks', is_flag=True)
@click.option('--expand-artist-to-related-artists', is_flag=True)
@click.option('--expand-artist-to-recommendations', is_flag=True)
@click.option('--expand-album-to-tracks', is_flag=True)
@click.option('--expand-album-to-artists', is_flag=True)
@click.option('--expand-playlist-to-tracks', is_flag=True)
@click.option('--expand-show-to-episodes', is_flag=True)
@click.option('--expand-genre-to-playlists', is_flag=True)
@click.option('--expand-genre-to-artists', is_flag=True)
@click.option('--expand-genre-to-related-genres', is_flag=True)
@click.option('--sort-artist-albums-by-keys', type=StringListParamType())
@click.option('--sort-artist-albums-reverse', is_flag=True)
@click.option('--exclude-various-artists-albums', is_flag=True)
@click.option('--exclude-uris', multiple=True)
@click.option('--include-album-groups', type=StringListParamType(),
              help='album, single, appears_on, compilation',
              default='album,single,compilation')
@click.option('--include-genre-playlists', type=StringListParamType(),
              default='intro,sound,female,year_2018,year_2019,pulse,edge')
@click.option('--looper-target-count', default=500)
@click.option('--looper-max-tries', default=10000)
@click.pass_context
def generate_playlist(ctx, **kwargs):
    # FIXME: subcommand --help calls this
    # https://github.com/pallets/click/issues/295
    # https://github.com/pallets/click/issues/814
    ctx.obj = PlaylistGenerator(**kwargs)


pass_generator = click.make_pass_decorator(PlaylistGenerator, ensure=True)


@generate_playlist.command()
@pass_generator
@click.argument('uris', required=True, nargs=-1)
def from_uris(generator,
              uris: tuple,
              progress: bool = False,
              **kwargs):
    generator.generate_from_uris(uris, **kwargs)


@generate_playlist.command()
@click.argument('query_type', type=click.Choice(['artist', 'album', 'track', 'playlist']))
@click.argument('query')
@pass_generator
def from_search(generator,
                query_type: str,
                query: str,
                **kwargs):
    generator.generate_from_search(query_type=query_type, query=query, **kwargs)


@generate_playlist.command()
@click.option('--seed-artist-uris', multiple=True)
@click.option('--seed-track-uris', multiple=True)
@click.option('--seed-genres', multiple=True)
@click.option('--attributes', 'attributes_list', multiple=True)
@pass_generator
def from_recommendations(
        generator,
        seed_artist_uris: tuple = None,
        seed_track_uris: tuple = None,
        seed_genres: tuple = None,
        attributes_list: tuple = None,
        **kwargs
        ):

    '''generate playlist from recommendation'''
    attributes_dict: Dict[str, Union[float, int]] = {}
    if attributes_list is not None:
        attributes_dict = {k: v for k, v in (x.split(':') for x in attributes_list)}
        tekore.client.api.browse.validate_attributes(attributes_dict)
    generator.generate_from_recommendations(
        seed_artist_uris=seed_artist_uris,
        seed_track_uris=seed_track_uris,
        seed_genres=seed_genres,
        seed_attributes=attributes_dict,
        **kwargs)


@generate_playlist.command()
@click.argument('genre_name', required=True, nargs=-1,
                autocompletion=toukka.sopiva.spotify_manager.genres.click_genre_completer)
@pass_generator
def from_genres(
        generator,
        genre_name: tuple,
        **kwargs
        ):

    genres = toukka.sopiva.spotify_manager.genres.genres()
    genres_list = list()
    for name in genre_name:
        genre = genres.get(name)
        if genre is None:
            raise click.ClickException(f'genre "{name}" not found')
        logger.debug(genre)
        genres_list.append(genre)
    generator.generate_from_genres(genres=genres_list, **kwargs)


@generate_playlist.command()
@click.argument('genre_name_re', required=True)
def from_genres_re(
        genre_name_re: str,
        **kwargs
        ):
    regex = re.compile(genre_name_re)
    genres = toukka.sopiva.spotify_manager.genres.genres()
    genre_names_match = filter(regex.fullmatch, genres.keys())
    context = click.get_current_context()
    context.invoke(from_genres, genre_name=genre_names_match, **kwargs)


@generate_playlist.command()
@click.option('--market')
@click.option('--filter-by-genre', multiple=True)
@click.option('--filter-by-no-genre', is_flag=True)
@click.option('--filter-by-genre-contains', multiple=True)
@click.option('--filter-by-artist-played-count', type=int)
@click.option('--filter-by-album-type')
@click.option('--filter-mode')
@click.option('--sort-by-release-date', is_flag=True)
@click.option('--sort-by-album-type', is_flag=True)
@click.option('--sort-reversed', is_flag=True)
def from_new_releases(
        market: str = None,
        filter_by_genre: tuple = None,
        filter_by_genre_contains: tuple = None,
        filter_by_no_genre: bool = None,
        filter_by_artist_played_count: int = None,
        filter_by_album_type: str = None,
        filter_mode: str = None,
        sort_by_release_date: bool = False,
        sort_by_album_type: bool = False,
        sort_reversed: bool = False
        ):

    albums = search_new_releases(**locals())
    uris = list()
    for album in albums:
        uris.append(album.uri)
    context = click.get_current_context()
    context.invoke(from_uris, uris=uris)


@generate_playlist.command()
@click.argument('uris', required=True, nargs=-1)
def easy_uris(uris: tuple):
    '''easy shortcut to from-uris'''
    kwargs_for_uris = {
        'expand_playlist_to_tracks': True,
        'expand_track_to_album': True,
        'expand_album_to_tracks': True,
        'expand_artist_to_albums': True,
        'expand_artist_to_related_artists': True
    }
    context = click.get_current_context()
    context.invoke(from_uris, uris=uris, **kwargs_for_uris)


@generate_playlist.command()
@click.argument('genre_name', required=True, nargs=-1,
                autocompletion=toukka.sopiva.spotify_manager.genres.click_genre_completer)
def easy_genres(genre_name: tuple):
    '''easy shortcut to from-genres'''
    kwargs_for_playlist = {
        'expand_playlist_to_tracks': True,
        'expand_track_to_album': True,
        'expand_album_to_tracks': True,
        'expand_track_to_artists': False,
        'expand_artist_to_albums': False
    }
    context = click.get_current_context()
    context.invoke(from_genres, genre_name=genre_name, **kwargs_for_playlist)


# END
