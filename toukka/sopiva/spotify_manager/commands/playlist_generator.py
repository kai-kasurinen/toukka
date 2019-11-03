#
#

import logging
import pprint
import dataclasses

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
    ctx.obj = PlaylistGenerator(**kwargs)


pass_generator = click.make_pass_decorator(PlaylistGenerator, ensure=True)


@generate_playlist.command()
@pass_generator
@click.argument('uris', required=True, nargs=-1)
def from_uris(generator,
              uris: list):
    generator.generate_from_uris(uris)


@generate_playlist.command()
@click.argument('query_type', type=click.Choice(['artist', 'album', 'track', 'playlist']))
@click.argument('query')
@pass_generator
def from_search(generator,
                query_type: str,
                query: str):
    generator.generate_from_search(query_type=query_type, query=query)


@generate_playlist.command()
@click.option('--seed-artist-uris', multiple=True)
@click.option('--seed-track-uris', multiple=True)
@click.option('--seed-genres', multiple=True)
@click.option('--attributes', 'attributes_list', multiple=True)
@pass_generator
def from_recommendations(generator,
                         seed_artist_uris: list = None,
                         seed_track_uris: list = None,
                         seed_genres: list = None,
                         attributes_list: list = None):

    '''generate playlist from recommendation'''
    attributes_dict = {}
    if attributes_list is not None:
        attributes_dict = {k: v for k, v in (x.split(':') for x in attributes_list)}
        spotipy.client.browse.validate.validate_attributes(attributes_dict)
    generator.generate_from_recommendations(
        seed_artist_uris=seed_artist_uris,
        seed_track_uris=seed_track_uris,
        seed_genres=seed_genres,
        seed_attributes=attributes_dict)


@generate_playlist.command()
@click.argument('genre_name', required=True, nargs=-1,
                autocompletion=toukka.sopiva.spotify_manager.genres.click_genre_completer)
@pass_generator
def from_genres(generator,
                genre_name: list):
    genres = toukka.sopiva.spotify_manager.genres.genres()

    uris_all = list()
    for name in genre_name:
        genre = genres.get(name)
        if genre is None:
            raise Exception(f'genre "{name}" not found')
        print(genre)
        playlists = dataclasses.asdict(genre.playlists)
        uris = [uri for uri in playlists.values() if uri is not None]
        uris_all.extend(uris)

    generator.generate_from_uris(uris=uris_all)


# END
