#

import argh
import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer import first as printer


def categories(country: str = None,
               locale: str = None):
    '''list categories'''
    spotify = get_spotify()
    paging = spotify.categories(country=country, locale=locale, limit=50)
    print(f'found {paging.total} categories')
    categories = spotify.items_from_paging(paging)
    for category in categories:
        print(f'{category.id:20}: {category.name}')


def featured_playlists(country: str = None,
                       locale: str = None,
                       timestamp: str = None):
    '''list categories'''
    spotify = get_spotify()
    message, paging = spotify.featured_playlists(
        country=country,
        locale=locale,
        timestamp=timestamp,
        limit=50)
    print(f'message: {message}')
    print(f'found {paging.total} featured playlists')
    playlists = spotify.all_items_from_paging(paging)
    for playlist in playlists:
        print(f'{playlist.id}: {playlist.name}')


def recommendation_genre_seeds():
    '''get list of available genre seeds'''
    return get_spotify().recommendation_genre_seeds()


@argh.arg('--seed-artist-uris', nargs='*')
@argh.arg('--seed-track-uris', nargs='*')
@argh.arg('--seed-genres', nargs='*')
def recommendations(seed_artist_uris: list = None,
                    seed_track_uris: list = None,
                    seed_genres: list = None,
                    market: str = None,
                    limit: int = 100):
    '''get a list of recommended tracks for seeds'''

    def uris_to_ids(uris: list):
        ids = list()
        for uri in uris:
            uri_type, uri_id = spotipy.convert.from_uri(uri)
            ids.append(uri_id)
        return ids

    seed_artist_ids = None
    seed_track_ids = None
    if seed_artist_uris is not None:
        seed_artist_ids = uris_to_ids(seed_artist_uris)
    if seed_track_uris is not None:
        seed_track_ids = uris_to_ids(seed_artist_uris)

    spotify = get_spotify()
    # TODO: support attributes
    attributes = dict()
    recommendations = spotify.recommendations(
                                            artist_ids=seed_artist_ids,
                                            track_ids=seed_track_ids,
                                            genres=seed_genres,
                                            market=market,
                                            limit=limit,
                                            **attributes)

    for seed in recommendations.seeds:
        printer.printer(seed)

    for track in recommendations.tracks:
        printer.printer(track)

#

COMMANDS = [
    categories,
    featured_playlists,
    recommendation_genre_seeds,
    recommendations
]

# END
