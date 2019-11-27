#

import logging
import re
import itertools
import pickle
import os

from dataclasses import dataclass
from typing import List, Optional

from xdg.BaseDirectory import save_cache_path
from bs4 import BeautifulSoup

import spotipy.convert

import toukka.cache.dogpile
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


"""
@dataclass(frozen=True)
class GenrePlaylists:
    intro: Optional[str] = None
    sound: Optional[str] = None
    pulse: Optional[str] = None
    edge: Optional[str] = None
    female: Optional[str] = None
    year_2018: Optional[str] = None
    year_2019: Optional[str] = None
"""


class GenrePlaylists(dict):
    pass


@dataclass(frozen=True)
class Genre:
    name: str
    playlists: Optional[GenrePlaylists] = None
    related: Optional[List[Optional[str]]] = None


# TODO: make somehow frozen
class Genres(dict):
    pass


# TODO: fix caching, currently it caches ~1.7GiB

def genres_make():
    spotify = get_spotify()

    sound_of_spotify_id = 'thesoundsofspotify'
    particle_detector_id = 'particledetector'
    particle_filter_id = 'particlefilter'
    particle_detector_2018_id = 'particledetector2018'
    particle_detector_2019_id = 'particledetector2019'

    # TODO: move to Spotify
    @toukka.cache.dogpile.local.cache_on_arguments()
    def playlists_cached(user_id: str):
        paging = spotify.playlists(user_id, limit=50)
        logger.debug('playlists total: %i', paging.total)
        playlists = list(spotify.all_items_from_paging(paging))
        return playlists

    @toukka.cache.dogpile.local.cache_on_arguments()
    def playlist_cached(playlist_id: str):
        return spotify.playlist(playlist_id, market=None)

    # @toukka.cache.dogpile.local.cache_on_arguments(expiration_time=604800)
    def process_sound_of_spotify():
        user_id = sound_of_spotify_id
        logger.info('processing user: %s', user_id)
        playlists = playlists_cached(user_id)
        logger.info('%s playlists count: %i', user_id, len(playlists))
        sounds = dict()
        places = dict()
        related = dict()

        for playlist in playlists:
            if playlist.owner.id != user_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue

            if playlist.name.startswith('The Sound of'):
                thing = playlist.name.split('The Sound of ')[1]
                logger.debug(f'thing: {thing}')

                if playlist.description.startswith('See also'):
                    genre_name = thing.lower()
                    sounds[genre_name] = playlist.uri

                    desc_parts = playlist.description.split(sep='; ')
                    related_genres = list()

                    for desc_part in desc_parts:

                        if desc_part.startswith('See also'):
                            # TODO: parse and use
                            # intro, pulse, edge, female, year
                            pass

                        elif (desc_part.startswith('or the Sounds of')
                              or desc_part.startswith('or the Sound of')):
                            soup = BeautifulSoup(desc_part, features='html.parser')
                            for link in soup.find_all('a'):
                                related_genres.append(link.string.lower())
                            related[genre_name] = related_genres
                            # logger.debug('%s related to %s', genre_name, related_genres)

                        elif desc_part.startswith('or much more at'):
                            # link to evernoise
                            pass

                        else:
                            logger.warning('%s: not supported desc part: %s', playlist.uri, desc_part)

                elif playlist.description.startswith('The songs that define'):
                    places[thing] = playlist.uri
                elif playlist.description.startswith('See much more at'):
                    # only link to evernoise
                    pass
                else:
                    logger.debug('%s: not supported desc: %s', playlist.uri, playlist.description)

            elif playlist.name.startswith('The Needle'):
                pass
            elif playlist.name.startswith('House Concert'):
                pass
            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)
        return sounds, places, related

    # @toukka.cache.dogpile.local.cache_on_arguments(expiration_time=604800)
    def process_particle_detector():
        user_id = particle_detector_id
        logger.info('processing user: %s', user_id)
        playlists = playlists_cached(user_id)
        logger.info('%s playlists count: %i', user_id, len(playlists))
        intros = dict()
        pulses = dict()
        edges = dict()
        for playlist in playlists:
            if playlist.owner.id != user_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue

            if playlist.name.startswith('Intro to'):
                thing = playlist.name.split('Intro to ')[1]
                genre_name = thing.lower()
                intros[genre_name] = playlist.uri

            elif playlist.name.startswith('The Pulse of'):
                thing = playlist.name.split('The Pulse of ')[1]
                genre_name = thing.lower()
                pulses[genre_name] = playlist.uri

            elif playlist.name.startswith('The Edge of'):
                thing = playlist.name.split('The Edge of ')[1]
                genre_name = thing.lower()
                edges[genre_name] = playlist.uri

            elif playlist.name.startswith('Metafilter'):
                pass
            elif playlist.name.startswith('Metaedge'):
                pass
            elif playlist.name.startswith('Metapulse'):
                pass

            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)

        return intros, pulses, edges

    # @toukka.cache.dogpile.local.cache_on_arguments(expiration_time=604800)
    def process_particle_filter():
        user_id = particle_filter_id
        logger.info('processing user: %s', user_id)
        playlists = playlists_cached(user_id)
        logger.info('%s playlists count: %i', user_id, len(playlists))
        females = dict()
        for playlist in playlists:
            if playlist.owner.id != user_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue
            if playlist.name.startswith('A ♀Filter for'):
                thing = playlist.name.split('A ♀Filter for ')[1]
                genre_name = thing.lower()
                females[genre_name] = playlist.uri
            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)
        return females

    # @toukka.cache.dogpile.local.cache_on_arguments(expiration_time=604800)
    def process_particle_detector_year(user_id: str, year: int):
        logger.info('processing user: %s, year: %i', user_id, year)
        playlists = playlists_cached(user_id)
        logger.info('%s playlists count: %i', user_id, len(playlists))
        ret = Genres()
        for playlist in playlists:
            if playlist.owner.id != user_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue

            if playlist.name.startswith('%i in' % year):
                thing = playlist.name.split('%i in ' % year)[1]
                genre_name = thing.lower()
                ret[genre_name] = playlist.uri
            elif playlist.name.startswith('The Sound of'):
                # place year
                pass
            elif playlist.name.startswith('Meta%i' % year):
                pass
            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)
        return ret

    #
    logger.info('generating genres, this may take some time')

    sounds, places, related = process_sound_of_spotify()
    intros, pulses, edges = process_particle_detector()
    females = process_particle_filter()
    year_2018 = process_particle_detector_year(particle_detector_2018_id, 2018)
    year_2019 = process_particle_detector_year(particle_detector_2019_id, 2019)
    genres = Genres()

    for genre_name in sounds.keys():

        genre_playlists = GenrePlaylists(
            intro=intros.get(genre_name),
            sound=sounds.get(genre_name),
            pulse=pulses.get(genre_name),
            edge=edges.get(genre_name),
            female=females.get(genre_name),
            year_2018=year_2018.get(genre_name),
            year_2019=year_2019.get(genre_name)
            )

        genre = Genre(
            name=genre_name,
            playlists=genre_playlists,
            related=related.get(genre_name)
            )

        genres[genre.name] = genre

    # TODO: do something with places
    logger.info('places total: %i', len(places))
    logger.info('genres total: %i', len(genres))
    return genres


# FIXME: rename
def genres() -> Genres:
    try:
        return genres_load()
    except FileNotFoundError:
        logger.warning('pickled genres not found, returning empty')
        return Genres()


def genres_refresh() -> None:
    genres_save()


def genres_save() -> None:
    genres = genres_make()
    _file = os.path.join(save_cache_path('toukka', 'spotify'), 'genres.pickle')
    with open(_file, 'wb') as file:
        pickle.dump(genres, file)


def genres_load() -> Genres:
    _file = os.path.join(save_cache_path('toukka', 'spotify'), 'genres.pickle')
    with open(_file, 'rb') as file:
        return pickle.load(file)


# NOTE: for argcomplete
def argcomplete_genre_completer(prefix, **kwargs):
    _genres = genres().keys()
    return (genre for genre in _genres if genre.startswith(prefix))


# NOTE: for click
# FIXME: not work?
#
# ctx - The current click context.
# args - The list of arguments passed in.
# incomplete - The partial word that is being completed, as a string.
#              May be an empty string '' if no characters have been entered yet.
def click_genre_completer(ctx, args, incomplete):
    return argcomplete_genre_completer(incomplete)

# END
