#
#

import logging
import pprint

import argh
import spotipy.convert

from toukka.sopiva.spotify_manager.playlist_generator import PlaylistGenerator


@argh.arg('uris', nargs='*')
def generate_playlist_from_uris(uris: list,
                                dry_run: bool = False,
                                expand_track_to_album: bool = False,
                                expand_track_to_artist: bool = False,
                                expand_artist_to_albums: bool = False,
                                expand_artist_to_top_tracks: bool = False,
                                expand_artist_to_related_artists: bool = False,
                                expand_album_to_tracks: bool = False,
                                expand_playlist_to_tracks: bool = False,
                                expand_generator_to_items: bool = False):
    print(locals())
    generator = PlaylistGenerator()
    generator.generate_playlist_from_uris(**locals())


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
    print(locals())
    generator = PlaylistGenerator()
    generator.generate_playlist_from_search(**locals())


# FIXME: update
@argh.arg('--seed-artist-uris', nargs='*')
@argh.arg('--seed-track-uris', nargs='*')
@argh.arg('--seed-genres', nargs='*')
def generate_playlist_from_recommendation(seed_artist_uris: list = None,
                                          seed_track_uris: list = None,
                                          seed_genres: list = None,
                                          call_times: int = 1,
                                          expand_track_to_album: bool = False,
                                          expand_track_to_artist: bool = False,
                                          expand_generator_to_items: bool = False,
                                          dry_run: bool = False):
    '''generate playlist from recommendation'''
    generator = PlaylistGenerator()
    generator.generate_playlist_from_recommendations(**locals())


COMMANDS = [
    generate_playlist_from_uris,
    generate_playlist_from_search,
    generate_playlist_from_recommendation,
]


# END
