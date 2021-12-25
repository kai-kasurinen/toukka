#

import logging

import toukka.sopiva.spotify.printer.first

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.metabrainz import musicbrainzngs
from toukka.printer.first import printer

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)


def print_currently_listening():
    spotify = get_spotify()

    currently_playing = spotify.playback_currently_playing()

    if currently_playing.currently_playing_type.name == 'track':
        track = currently_playing.item
    else:
        print('Not playing...')
        return

    # printer(track)

    # release
    album = track.album
    print(f'searching album ({album.uri})...')
    album_url = spotify.convert.to_url(track.album.type, track.album.id)
    album_mbids = get_entity_mbids_by_url('release', album_url)
    print(f'... found {len(album_mbids)} mbids')

    # artists
    for artist in track.artists:
        # printer(artist)
        print(f'searching artist {artist.name} ({artist.uri}) ...')
        artist_url = spotify.convert.to_url(artist.type, artist.id)
        artist_mbids = get_entity_mbids_by_url('artist', artist_url)
        print(f'... found {len(artist_mbids)} mbids')





def get_entity_mbids_by_url(entity_type, url):
    logger.debug('get entity (%s) mbids by url %s', entity_type, url)

    try:
        result = musicbrainzngs.browse_urls(
            resource=url,
            includes=musicbrainzngs.VALID_BROWSE_INCLUDES.get('url'))
    except musicbrainzngs.musicbrainz.ResponseError as error:
        if error.cause.code == 404:
            logger.debug('not found')
            return []
        else:
            raise

    mbids = list()

    if result:
        logger.debug('found %s relations from musicbrainz', len(result.get('relations')))
        for relation in result.get('relations'):
            target_type = relation.get('target-type')
            if target_type == entity_type:
                mbids.append(relation.get(entity_type).get('id'))
            else:
                logger.debug('wrong target_type (%s != %s) on relation', target_type, entity_type)
    else:
        logger.debug('failed, no result')

    return mbids


# END
