#

import logging
import re
import itertools
import pickle
import os

import unidecode
import tekore

from dataclasses import dataclass
from typing import List, Optional

# TODO: use appdirs instead?
from xdg.BaseDirectory import save_cache_path
from bs4 import BeautifulSoup

# import toukka.cache.dogpile
from toukka.sopiva.spotify.util import get_spotify
from toukka.printer import printer

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
    name_ascii: str
    playlists: Optional[GenrePlaylists] = None
    related: Optional[List[Optional[str]]] = None


# TODO: make somehow frozen
class Genres(dict):
    pass


@printer.register
def print_genre(genre: Genre):
    print(f'genre: {genre.name}')
    # only lists available playlist names
    playlist_keys = list(filter(genre.playlists.get, genre.playlists))
    print(f'\tplaylists: {playlist_keys}')
    print(f'\trelated: {genre.related}')


def genres_make():

    def process_sound_of_spotify(user_id: str):

        logger.info('processing user: %s', user_id)
        playlists = spotify.playlists_all_list_cached(user_id)
        logger.info('%s playlists count: %i', user_id, len(playlists))

        sounds = dict()
        places = dict()
        related = dict()

        for playlist in playlists:

            if playlist.owner.id != user_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue

            if not playlist.description:
                logger.warning('%s: no description', playlist.uri)

            if playlist.name.startswith('The Sound of'):
                thing = playlist.name.split('The Sound of ')[1]
                logger.debug(f'thing: {thing}')

                if playlist.description.startswith('See also'):
                    genre_name = thing.lower()
                    sounds[genre_name] = playlist.uri

                    desc_parts = playlist.description.split(sep='; ')
                    related_genres = list()

                    for desc_part in desc_parts:

                        if (desc_part.startswith('See also the Sounds of')
                                or desc_part.startswith('or the Sounds of')
                                or desc_part.startswith('or the Sound of')):

                            # TODO: move to function
                            soup = BeautifulSoup(desc_part, features='html.parser')
                            for link in soup.find_all('a'):
                                related_genres.append(link.string.lower())
                            related[genre_name] = related_genres
                            # logger.debug('%s related to %s', genre_name, related_genres)

                        elif desc_part.startswith('See also'):
                            # NOTE: 'See also' can be:
                            # NOTE: - related genres
                            # NOTE: - intro, pulse, edge, female, year playlists
                            pass

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

        logger.info('%s, found %i sounds, %i places, %s related',
                    user_id, len(sounds), len(places), len(related))

        return sounds, places, related

    def process_particle_detector(user_id: str):

        logger.info('processing user: %s', user_id)
        playlists = spotify.playlists_all_list_cached(user_id)
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

        logger.info('%s, found %i intros, %i pulses, %s edges',
                    user_id, len(intros), len(pulses), len(edges))

        return intros, pulses, edges

    def process_particle_filter(user_id: str):

        logger.info('processing user: %s', user_id)
        playlists = spotify.playlists_all_list_cached(user_id)
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

        logger.info('%s, found %i females',
                    user_id, len(females))

        return females

    def process_particle_detector_year(user_id: str, year: int):

        logger.info('processing user: %s, year: %i', user_id, year)
        try:
            playlists = spotify.playlists_all_list_cached(user_id)
        except tekore.BadGateway as e:
            logger.error(e)
            return Genres()
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

        logger.info('%s, found %i',
                    user_id, len(ret))

        return ret

    # main

    logger.info('generating genres, this may take some time')

    spotify = get_spotify(token_type='client')

    sound_of_spotify_id = 'thesoundsofspotify'
    particle_detector_id = 'particledetector'
    particle_introductor_id = 'particleintroductor'
    particle_filter_id = 'particlefilter'

    sounds, places, related = process_sound_of_spotify(sound_of_spotify_id)
    # NOTE: intros is empty
    intros, pulses, edges = process_particle_detector(particle_detector_id)

    # FIXME: cleanup
    if not intros:
        logger.info('no intros, trying different user')
        intros, pulses_, edges_ = process_particle_detector(particle_introductor_id)

    females = process_particle_filter(particle_filter_id)

    years_range = range(2018, 2025)
    years = dict()

    for year in years_range:
        years[year] = process_particle_detector_year(f'particledetector{year}', year)

    genres = Genres()

    logger.info('...')

    for genre_name in sounds.keys():

        genre_playlists = GenrePlaylists(
            intro=intros.get(genre_name),
            sound=sounds.get(genre_name),
            pulse=pulses.get(genre_name),
            edge=edges.get(genre_name),
            female=females.get(genre_name),
            )

        # grrrr
        for year in years_range:
            genre_playlists[f'year_{year}'] = years[year].get(genre_name)

        genre_name_unicode = genre_name
        genre_name_ascii = unidecode.unidecode(genre_name_unicode)

        if genre_name_ascii != genre_name_unicode:
            logger.warning('%s != %s', genre_name_ascii, genre_name_unicode)

        genre = Genre(
            name=genre_name_unicode,
            name_ascii=genre_name_ascii,
            playlists=genre_playlists,
            related=related.get(genre_name)
            )

        genres[genre.name] = genre

    # TODO: do something with places
    logger.info('places total: %i', len(places))
    logger.info('genres total: %i', len(genres))
    return genres


def _get_genres_filename():
    return os.path.join(save_cache_path('toukka', 'spotify_manager'), 'genres.pickle')


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
    _file = _get_genres_filename()
    with open(_file, 'wb') as file:
        pickle.dump(genres, file)


def genres_load() -> Genres:
    _file = _get_genres_filename()
    with open(_file, 'rb') as file:
        return pickle.load(file)


def get_genres_list():
    g = genres()
    g_list = list(g.keys())
    return g_list


def genres_re(name_re: str):
    regex = re.compile(name_re)
    genres_ = genres()

    # NOTE:
    # If the whole string matches this regular expression,
    # return a corresponding match object.
    # Return None if the string does not match the pattern
    #
    # match object is True and None is False
    genre_names_match = list(filter(regex.fullmatch, genres_.keys()))

    # TODO: return list(Genres), not just names
    return genre_names_match




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
