#

import click

# TODO: remove?
import tekore._client.api.browse

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer import first as printer
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.group()
def browse():
    pass


@browse.command()
@click.option('--country')
@click.option('--locale')
def featured_playlists(country: str = None,
                       locale: str = None,
                       timestamp: str = None):
    '''Get a list of Spotify featured playlists'''
    spotify = get_spotify()
    message, paging = spotify.featured_playlists(
        country=country,
        locale=locale,
        timestamp=timestamp)
    print(f'message: {message}')
    print(f'found {paging.total} featured playlists')
    playlists = spotify.all_items(paging)
    for playlist in playlists:
        printer(playlist)


@browse.command()
@click.option('--country')
def new_releases(country: str = None):
    '''Get a list of new album releases featured in Spotify'''
    spotify = get_spotify()
    paging = spotify.new_releases(country=country)
    print(f'found {paging.total} releases')
    for album in spotify.all_items(paging):
        printer(album)


@browse.command()
@click.option('--country')
@click.option('--locale')
def categories(country: str = None,
               locale: str = None):
    '''Get a list of categories used to tag items in Spotify'''
    spotify = get_spotify()
    paging = spotify.categories(country=country, locale=locale)
    print(f'found {paging.total} categories')
    for category in spotify.all_items(paging):
        printer(category)


@browse.command()
@click.argument('category_id')
@click.option('--country')
@click.option('--locale')
def category(category_id: str,
             country: str = None,
             locale: str = None):
    '''Get a single category used to tag items in Spotify'''
    spotify = get_spotify()
    category = spotify.category(category_id, country=country, locale=locale)
    printer(category)


@browse.command()
@click.argument('category_id')
@click.option('--country')
def category_playlists(category_id: str,
                       country: str = None):
    '''Get a list of Spotify playlists tagged with a particular category'''
    spotify = get_spotify()
    paging = spotify.category_playlists(
        category_id,
        country=country)
    print(f'found {paging.total} playlists')
    playlists = spotify.all_items(paging)
    for playlist in playlists:
        printer(playlist)


@browse.command()
@click.option('--seed-artist-uris', multiple=True)
@click.option('--seed-track-uris', multiple=True)
@click.option('--seed-genres', multiple=True)
@click.option('--attributes', multiple=True)
@click.option('--market')
def recommendations(seed_artist_uris: list = None,
                    seed_track_uris: list = None,
                    seed_genres: list = None,
                    attributes: list = None,
                    market: str = None):
    '''get a list of recommended tracks for seeds'''
    print(locals())

    spotify = get_spotify()

    def uris_to_ids(uris: list):
        ids = list()
        for uri in uris:
            uri_type, uri_id = spotify.convert.from_uri(uri)
            ids.append(uri_id)
        return ids

    seed_artist_ids = None
    seed_track_ids = None
    if seed_artist_uris is not None:
        seed_artist_ids = uris_to_ids(seed_artist_uris)
    if seed_track_uris is not None:
        seed_track_ids = uris_to_ids(seed_track_uris)

    # FIXME: remove this hack
    attributes_list = attributes
    attributes_dict = {}
    if attributes_list is not None:
        attributes_dict = {k: v for k, v in (x.split(':') for x in attributes_list)}
        print(attributes_dict)
        tekore.client.api.browse.validate_attributes(attributes_dict)

    recommendations = spotify.recommendations(
        artist_ids=seed_artist_ids,
        track_ids=seed_track_ids,
        genres=seed_genres,
        market=market,
        **attributes_dict)

    for seed in recommendations.seeds:
        printer(seed)

    for track in recommendations.tracks:
        printer(track)


@browse.command()
def recommendation_genre_seeds():
    '''get list of available genre seeds'''
    for genre in get_spotify().recommendation_genre_seeds():
        print(genre)


# END
