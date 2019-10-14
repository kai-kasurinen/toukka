#
#

import logging
import pprint

import argh
import spotipy.convert

from toukka.sopiva.spotify_manager.playlist_generator import PlaylistGenerator


def generate_playlist_from_artist(artist_uri):
    artist_uri_type, artist_uri_id = spotipy.convert.from_uri(artist_uri)
    generator = PlaylistGenerator()
    generator.generate_playlist_from_artist_id(artist_uri_id)


def generate_playlist_from_related_artists(artist_uri):
    artist_uri_type, artist_uri_id = spotipy.convert.from_uri(artist_uri)
    generator = PlaylistGenerator()
    generator.generate_playlist_from_related_artists(artist_uri_id)


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


def generate_playlist_from_playlist(playlist_uri,
                                    expand_albums: bool = False,
                                    expand_artists: bool = False):
    playlist_uri_type, playlist_uri_id = spotipy.convert.from_uri(playlist_uri)
    generator = PlaylistGenerator()
    generator.generate_playlist_from_playlist_id(playlist_uri_id,
                                                 expand_albums=expand_albums,
                                                 expand_artists=expand_artists)


@argh.arg('type', choices=['artist', 'album', 'track', 'playlist'])
def generate_playlist_from_search(type: str, query: str):
    generator = PlaylistGenerator()
    generator.add_source(generator.iterate_search(query_type=type, query=query))
    generator.generate()


#

COMMANDS = [
    generate_playlist_from_artist,
    generate_playlist_from_playlist,
    generate_playlist_from_recommendation,
    generate_playlist_from_related_artists,
    generate_playlist_from_search
]


# END
