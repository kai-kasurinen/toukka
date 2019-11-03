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


@cli_root.group()
def generate_playlist():
    pass


@generate_playlist.command('from-uris')
@click.argument('uris', required=True, nargs=-1)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--randomize', is_flag=True, default=False)
def generate_playlist_from_uris(uris: list,
                                dry_run: bool = False,
                                randomize: bool = False,
                                expand_track_to_album: bool = False,
                                expand_track_to_artist: bool = False,
                                expand_track_to_recommendations: bool = False,
                                expand_artist_to_albums: bool = False,
                                expand_artist_to_top_tracks: bool = False,
                                expand_artist_to_related_artists: bool = False,
                                expand_artist_to_recommendations: bool = False,
                                expand_album_to_tracks: bool = False,
                                expand_playlist_to_tracks: bool = False,
                                expand_generator_to_items: bool = False):
    args = locals()
    print(args)
    generator = PlaylistGenerator()
    generator.generate_from_uris(**args)


@generate_playlist.command('from-search')
@click.argument('query_type', type=click.Choice(['artist', 'album', 'track', 'playlist']))
@click.argument('query')
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--randomize', is_flag=True, default=False)
def generate_playlist_from_search(query_type: str, query: str,
                                  dry_run: bool = False,
                                  randomize: bool = False,
                                  expand_track_to_album: bool = False,
                                  expand_track_to_artist: bool = False,
                                  expand_track_to_recommendations: bool = False,
                                  expand_artist_to_albums: bool = False,
                                  expand_artist_to_top_tracks: bool = False,
                                  expand_artist_to_related_artists: bool = False,
                                  expand_artist_to_recommendations: bool = False,
                                  expand_album_to_tracks: bool = False,
                                  expand_playlist_to_tracks: bool = False,
                                  expand_generator_to_items: bool = False):
    args = locals()
    print(args)
    generator = PlaylistGenerator()
    generator.generate_from_search(**args)


@generate_playlist.command('from-recomendations')
@click.option('--seed-artist-uris', multiple=True)
@click.option('--seed-track-uris', multiple=True)
@click.option('--seed-genres', multiple=True)
@click.option('--attributes', multiple=True)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--randomize', is_flag=True, default=False)
def generate_playlist_from_recommendations(seed_artist_uris: list = None,
                                           seed_track_uris: list = None,
                                           seed_genres: list = None,
                                           dry_run: bool = False,
                                           randomize: bool = False,
                                           recommendation_attributes_list: list = None,
                                           expand_track_to_album: bool = False,
                                           expand_track_to_artist: bool = False,
                                           expand_track_to_recommendations: bool = False,
                                           expand_artist_to_albums: bool = False,
                                           expand_artist_to_top_tracks: bool = False,
                                           expand_artist_to_related_artists: bool = False,
                                           expand_artist_to_recommendations: bool = False,
                                           expand_album_to_tracks: bool = False,
                                           expand_playlist_to_tracks: bool = False,
                                           expand_generator_to_items: bool = False,
                                           **kwargs):
    '''generate playlist from recommendation'''
    args = locals()
    print(args)
    recommendation_attributes_dict = {}
    if recommendation_attributes_list is not None:
        recommendation_attributes_dict = {k: v for k, v in (x.split(':') for x in recommendation_attributes_list)}
        spotipy.client.browse.validate.validate_attributes(recommendation_attributes_dict)
    generator = PlaylistGenerator()
    generator.generate_from_recommendations(**args, recommendation_attributes=recommendation_attributes_dict)


@generate_playlist.command('from-genres')
@click.argument('genre_name', required=True, nargs=-1,
                autocompletion=toukka.sopiva.spotify_manager.genres.click_genre_completer)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--randomize', is_flag=True, default=False)
def generate_playlist_from_genres(genre_name: list,
                                  dry_run: bool = False,
                                  randomize: bool = False,
                                  expand_track_to_album: bool = False,
                                  expand_track_to_artist: bool = False,
                                  expand_artist_to_albums: bool = False,
                                  expand_artist_to_top_tracks: bool = False,
                                  expand_artist_to_related_artists: bool = False,
                                  expand_artist_to_recommendations: bool = False,
                                  expand_album_to_tracks: bool = False,
                                  expand_playlist_to_tracks: bool = False,
                                  expand_generator_to_items: bool = False
                                  ):
    args = locals()
    print(args)
    genres = toukka.sopiva.spotify_manager.genres.genres()

    uris_all = list()
    for name in genre_name:
        genre = genres.get(name)
        if genre is None:
            raise argh.exceptions.CommandError(f'genre "{name}" not found')
        print(genre)
        playlists = dataclasses.asdict(genre.playlists)
        uris = [uri for uri in playlists.values() if uri is not None]
        uris_all.extend(uris)

    generator = PlaylistGenerator()
    generator.generate_from_uris(uris=uris_all, **args)


# END
