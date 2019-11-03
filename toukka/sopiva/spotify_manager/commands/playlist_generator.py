#
#

import logging
import pprint
import dataclasses
import re

import click
import spotipy.convert
import spotipy.client.browse.validate

import toukka.sopiva.spotify_manager.genres

from toukka.sopiva.spotify_manager.playlist_generator import PlaylistGenerator
from toukka.sopiva.spotify_manager.cli import cli_root

logger = logging.getLogger(__name__)


@cli_root.group()
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--randomize', is_flag=True, default=False)
@click.option('--expand-track-to-album', is_flag=True)
@click.option('--expand-track-to-artists', is_flag=True)
@click.option('--expand-track-to-recommendations', is_flag=True)
@click.option('--expand-artist-to-albums', is_flag=True)
@click.option('--expand-artist-to-top-tracks', is_flag=True)
@click.option('--expand-artist-to-related-artists', is_flag=True)
@click.option('--expand-artist-to-recommendations', is_flag=True)
@click.option('--expand-album-to-tracks', is_flag=True)
@click.option('--expand-playlist-to-tracks', is_flag=True)
@click.option('--looper-target-count', default=500)
@click.option('--looper-max-tries', default=5000)
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
def from_recommendations(generator,
                         seed_artist_uris: tuple = None,
                         seed_track_uris: tuple = None,
                         seed_genres: tuple = None,
                         attributes_list: tuple = None,
                         **kwargs):

    '''generate playlist from recommendation'''
    attributes_dict = {}
    if attributes_list is not None:
        attributes_dict = {k: v for k, v in (x.split(':') for x in attributes_list)}
        spotipy.client.browse.validate.validate_attributes(attributes_dict)
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
def from_genres(generator,
                genre_name: tuple,
                **kwargs):
    genres = toukka.sopiva.spotify_manager.genres.genres()
    uris_all = list()
    for name in genre_name:
        genre = genres.get(name)
        if genre is None:
            raise click.ClickException(f'genre "{name}" not found')
        logger.debug(genre)
        playlists = dataclasses.asdict(genre.playlists)
        uris = [uri for uri in playlists.values() if uri is not None]
        uris_all.extend(uris)
    generator.generate_from_uris(uris=uris_all, **kwargs)


@generate_playlist.command()
@click.argument('genre_name_re', required=True)
@click.pass_context
def from_genres_re(ctx,
                   genre_name_re: str,
                   **kwargs):
    regex = re.compile(genre_name_re)
    genres = toukka.sopiva.spotify_manager.genres.genres()
    genre_names_match = filter(regex.fullmatch, genres.keys())
    ctx.invoke(from_genres, genre_name=genre_names_match, **kwargs)


@generate_playlist.command()
@click.argument('uris', required=True, nargs=-1)
@click.pass_context
def easy_uris(ctx,
              uris: tuple):
    '''easy shortcut to from-uris'''
    kwargs_for_uris = {
        'expand_playlist_to_tracks': True,
        'expand_track_to_album': True,
        'expand_album_to_tracks': True,
        'expand_artist_to_albums': True,
        'expand_artist_to_related_artists': True
    }
    ctx.invoke(from_uris, uris=uris, **kwargs_for_uris)


@generate_playlist.command()
@click.argument('genre_name', required=True, nargs=-1,
                autocompletion=toukka.sopiva.spotify_manager.genres.click_genre_completer)
@click.pass_context
def easy_genres(ctx,
                genre_name: tuple):
    '''easy shortcut to from-genres'''
    kwargs_for_playlist = {
        'expand_playlist_to_tracks': True,
        'expand_track_to_album': True,
        'expand_album_to_tracks': True,
        'expand_track_to_artists': False,
        'expand_artist_to_albums': False
    }
    ctx.invoke(from_genres, genre_name=genre_name, **kwargs_for_playlist)


# END
