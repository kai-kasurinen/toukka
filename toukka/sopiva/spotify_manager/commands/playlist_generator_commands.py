#
#

import logging
import pprint

import argh
import spotipy.convert

from toukka.sopiva.spotify_manager.playlist_generator_object import PlaylistGenerator


def generate_playlist_from_artist(artist_uri):
    artist_uri_type, artist_uri_id = spotipy.convert.from_uri(artist_uri)
    generator = PlaylistGenerator()
    generator.generate_playlist_from_artist_id(artist_uri_id)


def generate_playlist_from_recommendation_seeded_by_artists(artist_uri):
    artist_uri_type, artist_uri_id = spotipy.convert.from_uri(artist_uri)
    generator = PlaylistGenerator()
    generator.generate_playlist_from_recommendations(seed_artist_ids=[artist_uri_id])


#

COMMANDS = [
    generate_playlist_from_artist,
    generate_playlist_from_recommendation_seeded_by_artists
]


# END
