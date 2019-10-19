#
#

import logging
import pprint
import dataclasses

import argh
import spotipy.convert
import spotipy.client.browse.validate

import toukka.sopiva.spotify_manager.genres
from toukka.sopiva.spotify_manager.playlist_generator import PlaylistGenerator


def generate_playlist_from_uris(*uris: list,
                                dry_run: bool = False,
                                expand_track_to_album: bool = False,
                                expand_track_to_artist: bool = False,
                                expand_artist_to_albums: bool = False,
                                expand_artist_to_top_tracks: bool = False,
                                expand_artist_to_related_artists: bool = False,
                                expand_album_to_tracks: bool = False,
                                expand_playlist_to_tracks: bool = False,
                                expand_generator_to_items: bool = False):
    args = locals()
    print(args)
    generator = PlaylistGenerator()
    generator.generate_playlist_from_uris(**args)


@argh.arg('query_type', choices=['artist', 'album', 'track', 'playlist'])
def generate_playlist_from_search(query_type: str, query: str,
                                  dry_run: bool = False,
                                  expand_track_to_album: bool = False,
                                  expand_track_to_artist: bool = False,
                                  expand_artist_to_albums: bool = False,
                                  expand_artist_to_top_tracks: bool = False,
                                  expand_artist_to_related_artists: bool = False,
                                  expand_album_to_tracks: bool = False,
                                  expand_playlist_to_tracks: bool = False,
                                  expand_generator_to_items: bool = False):
    args = locals()
    print(args)
    generator = PlaylistGenerator()
    generator.generate_playlist_from_search(**args)


@argh.arg('--seed-artist-uris', nargs='*')
@argh.arg('--seed-track-uris', nargs='*')
@argh.arg('--seed-genres', nargs='*')
@argh.arg('--recommendation-attributes-list', nargs='*')
def generate_playlist_from_recommendations(seed_artist_uris: list = None,
                                           seed_track_uris: list = None,
                                           seed_genres: list = None,
                                           dry_run: bool = False,
                                           call_times: int = 1,
                                           recommendation_attributes_list: list = None,
                                           expand_track_to_album: bool = False,
                                           expand_track_to_artist: bool = False,
                                           expand_artist_to_albums: bool = False,
                                           expand_artist_to_top_tracks: bool = False,
                                           expand_artist_to_related_artists: bool = False,
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
    generator.generate_playlist_from_recommendations(**args, recommendation_attributes=recommendation_attributes_dict)


@argh.arg('genre_name', completer=toukka.sopiva.spotify_manager.genres.genres_completer)
def generate_playlist_from_genre(genre_name: str,
                                 dry_run: bool = False,
                                 expand_track_to_album: bool = False,
                                 expand_track_to_artist: bool = False,
                                 expand_artist_to_albums: bool = False,
                                 expand_artist_to_top_tracks: bool = False,
                                 expand_artist_to_related_artists: bool = False,
                                 expand_album_to_tracks: bool = False,
                                 expand_playlist_to_tracks: bool = False,
                                 expand_generator_to_items: bool = False
                                 ):
    args = locals()
    print(args)
    genres = toukka.sopiva.spotify_manager.genres.genres()
    genre = genres.get(genre_name)
    if genre is None:
        raise argh.exceptions.CommandError(f'genre "{genre_name}" not found')
    print(genre)
    playlists = dataclasses.asdict(genre.playlists)
    uris = [uri for uri in playlists.values() if uri is not None]
    generator = PlaylistGenerator()
    generator.generate_playlist_from_uris(uris=uris, **args)


COMMANDS = [
    generate_playlist_from_uris,
    generate_playlist_from_search,
    generate_playlist_from_recommendations,
    generate_playlist_from_genre
]


# END
