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


@dataclass
class Genre:
    name: str
    # TODO: move playlists to playlists dict
    sound: str = None
    intro: str = None
    pulse: str = None
    edge: str = None
    female: str = None


class Genres(dict):
    pass


def genres_make():
    spotify = get_spotify()

    sound_of_spotify_id = 'thesoundsofspotify'
    particle_detector_id = 'particledetector'
    particle_filter_id = 'particlefilter'
    # TODO: support years; name format '2018 in {genre}',
    #       also '2017 in {genre}' on particledetector
    particle_detector_2018_id = 'particledetector2018'

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
        playlists = playlists_cached(sound_of_spotify_id)
        logger.info('sound of spotify playlists len: %i', len(playlists))
        sounds = dict()
        for playlist in playlists:
            if playlist.owner.id != sound_of_spotify_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue

            if playlist.name.startswith('The Sound of'):
                thing = playlist.name.split('The Sound of ')[1]
                logger.debug(f'thing: {thing}')

                playlist_full = playlist_cached(playlist.id)
                playlist_destriction = playlist_full.description

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
        playlists = playlists_cached(particle_detector_id)
        logger.info('particle detector playlists len: %i', len(playlists))
        intros = dict()
        pulses = dict()
        edges = dict()
        for playlist in playlists:
            if playlist.owner.id != particle_detector_id:
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
        playlists = playlists_cached(particle_filter_id)
        logger.info('particle filter playlists len: %i', len(playlists))
        females = dict()
        for playlist in playlists:
            if playlist.owner.id != particle_filter_id:
                logger.warning('%s: not supported owner: %s', playlist.uri, playlist.owner.id)
                continue
            if playlist.name.startswith('A ♀Filter for'):
                thing = playlist.name.split('A ♀Filter for ')[1]
                genre_name = thing.lower()
                females[genre_name] = playlist.uri
            else:
                logger.warning('%s: not supported name: %s', playlist.uri, playlist.name)
        return females

    sounds = process_sound_of_spotify()
    intros, pulses, edges = process_particle_detector()
    females = process_particle_filter()
    genres = dict()

    for genre_name in sounds.keys():
        genre = Genre(name=genre_name,
                      sound=sounds.get(genre_name),
                      intro=intros.get(genre_name),
                      pulse=pulses.get(genre_name),
                      edge=edges.get(genre_name),
                      female=females.get(genre_name)
                      )
        genres[genre.name] = genre

    # and after loop
    logger.info('genres total: %i', len(genres))
    return genres


@toukka.cache.dogpile.region.cache_on_arguments(expiration_time=-1)
def genres():
    return genres_make()


def genres_refresh():
    return genres.refresh()


# END
