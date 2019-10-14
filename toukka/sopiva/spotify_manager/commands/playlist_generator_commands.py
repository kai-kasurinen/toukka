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
@argh.arg('--artist-uris', nargs='*')
@argh.arg('--track-uris', nargs='*')
@argh.arg('--genres', nargs='*')
def generate_playlist_from_recommendation(artist_uris: list = None,
                                          track_uris: list = None,
                                          genres: list = None,
                                          call_times: int = None,
                                          expand_albums: bool = False,
                                          expand_artists: bool = False,
                                          min_instrumentalness: float = None,
                                          max_instrumentalness: float = None,
                                          target_instrumentalness: float = None):
    '''generate playlist from recommendation'''
    def convert_uris_to_ids(uris):
        ret = list()
        for uri in uris:
            uri_type, uri_id = spotipy.convert.from_uri(uri)
            ret.append(uri_id)
        return ret

    params = dict()
    if artist_uris is not None:
        params['seed_artist_ids'] = convert_uris_to_ids(artist_uris)
    if track_uris is not None:
        params['seed_track_ids'] = convert_uris_to_ids(track_uris)
    if genres is not None:
        params['seed_genres'] = genres
    if call_times is not None:
        # FIXME: why str?
        params['call_times'] = int(call_times)
    if expand_albums is not None:
        params['expand_albums'] = expand_albums
    if expand_artists is not None:
        params['expand_artists'] = expand_artists

    # TODO: add min_/max_/target_ things when they are fixed from spotipy
    generator = PlaylistGenerator()
    generator.generate_playlist_from_recommendations(**params)


COMMANDS = [
    generate_playlist_from_recommendation,
    generate_playlist_from_search,
    generate_playlist_from_uris
]


# END
