#

import logging
import re
import itertools

from dataclasses import dataclass
from typing import List

import spotipy.convert

import toukka.cache.dogpile
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


@dataclass(frozen=True)
class GenrePlaylists:
    intro: str = None
    sound: str = None
    pulse: str = None
    edge: str = None
    female: str = None
    year_2018: str = None
    year_2019: str = None


@dataclass(frozen=True)
class Genre:
    name: str
    playlists: GenrePlaylists = None


class Genres(dict):
    pass


def genres_make():
    spotify = get_spotify()

    sound_of_spotify_id = 'thesoundsofspotify'
    particle_detector_id = 'particledetector'
    particle_filter_id = 'particlefilter'
    particle_detector_2018_id = 'particledetector2018'
    particle_detector_2019_id = 'particledetector2019'

    @toukka.cache.dogpile.region.cache_on_arguments(expiration_time=604800)
    def playlists_cached(user_id: str):
        paging = spotify.playlists(user_id, limit=50)
        logger.debug('playlists total: %i', paging.total)
        playlists = list(spotify.items_from_paging(paging))
        return playlists

    @toukka.cache.dogpile.region.cache_on_arguments(expiration_time=604800)
    def playlist_cached(playlist_id: str):
        return spotify.playlist(playlist_id, market=None)

    def process_sound_of_spotify():
        user_id = sound_of_spotify_id
        playlists = playlists_cached(user_id)
        logger.info('%s playlists count: %i', user_id, len(playlists))
        sounds = dict()
        for playlist in playlists:
            if playlist.owner.id != user_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue

            if playlist.name.startswith('The Sound of'):
                thing = playlist.name.split('The Sound of ')[1]
                logger.debug(f'thing: {thing}')

                playlist_full = playlist_cached(playlist.id)
                playlist_destriction = playlist_full.description

                # TODO: parse description and get see also genres

                if playlist_destriction.startswith('See also'):
                    genre_name = thing.lower()
                    sounds[genre_name] = playlist.uri
                elif playlist_destriction.startswith('The songs that define'):
                    # places?
                    pass
                else:
                    logger.warning('%s: not supported desc: %s', playlist.uri, playlist_destriction)

            elif playlist.name.startswith('The Needle'):
                pass
            elif playlist.name.startswith('House Concert'):
                pass
            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)
        return sounds

    def process_particle_detector():
        user_id = particle_detector_id
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
            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)

        return intros, pulses, edges

    def process_particle_filter():
        user_id = particle_filter_id
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

    # TODO: make generic for years
    def process_particle_detector_2018():
        user_id = particle_detector_2018_id
        playlists = playlists_cached(user_id)
        logger.info('%s playlists count: %i', user_id, len(playlists))
        year_2018 = dict()
        for playlist in playlists:
            if playlist.owner.id != user_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue
            if playlist.name.startswith('2018 in'):
                thing = playlist.name.split('2018 in ')[1]
                genre_name = thing.lower()
                year_2018[genre_name] = playlist.uri
            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)
        return year_2018

    def process_particle_detector_2019():
        user_id = particle_detector_2019_id
        playlists = playlists_cached(user_id)
        logger.info('%s playlists count: %i', user_id, len(playlists))
        year_2019 = dict()
        for playlist in playlists:
            if playlist.owner.id != user_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue
            if playlist.name.startswith('2019 in'):
                thing = playlist.name.split('2019 in ')[1]
                genre_name = thing.lower()
                year_2019[genre_name] = playlist.uri
            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)
        return year_2019

    sounds = process_sound_of_spotify()
    intros, pulses, edges = process_particle_detector()
    females = process_particle_filter()
    year_2018 = process_particle_detector_2018()
    year_2019 = process_particle_detector_2019()
    genres = dict()

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
            playlists=genre_playlists
            )

        genres[genre.name] = genre

    # and after loop
    logger.info('genres total: %i', len(genres))
    return genres


# TODO: use pickle?
@toukka.cache.dogpile.region.cache_on_arguments(expiration_time=-1)
def genres():
    return genres_make()


def genres_refresh():
    return genres.refresh()


def genres_completer(prefix, **kwargs):
    genres = toukka.sopiva.spotify_manager.genres.genres().keys()
    return (genre for genre in genres if genre.startswith(prefix))


# END
