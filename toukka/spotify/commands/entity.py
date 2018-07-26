#

'''spotify crowd site api commands'''

import argh

from toukka.toukka import Toukka
from toukka.utils import json_dump, json_dump_print


def entity(uri, dump=False):
    '''Get artist info'''
    toukka = Toukka()
    results = toukka.sp.crowd_site_entity(uri)
    entity = results.get('entity')

    if dump:
        return json_dump(entity)

    _print_entity(entity)


def _print_entity(entity):

    with_similar_artists=False
    with_images=False

    # on all types
    print('type: {type}'.format(**entity))
    print('name: {name}'.format(**entity))
    print('uri: {uri}'.format(**entity))
    print('gid: {gid}'.format(**entity))
    print('aliases: {aliases}'.format(**entity))
    print('categories: {categories}'.format(**entity))

    # on artist
    if entity.get('tags'):
        print('tags: {tags}'.format(**entity))

    # on all types
    if entity.get('external_urls'):
        print('urls:')
        for url in entity.get('external_urls'):
            print('\t{name}: {url}'.format(**url))

    if entity.get('type') == 'artist':
        print('locality: {origin_locality}, country: {origin_country}'.format(**entity))
        print('album_count: {album_count}, album_pages: {album_pages}'.format(**entity))
        # on artist
        if entity.get('bio'):
            print('bio: {bio:.80}'.format(**entity))


    if entity.get('similar_artists') and with_similar_artists:
        print('similar artists:')
        for artist in entity.get('similar_artists'):
            print('\t{artist_name}: {artist_uri}'.format(**artist))

    #
    if entity.get('images'):
        pass

    # 
    if entity.get('main_images') and with_images:
        print('main images:')
        for image in entity.get('main_images'):
            print('\t{width}x{height}: http:{url}'.format(**image))

    # on album
    if entity.get('group_members'):
        # display_group_gid, gid, name, album_type, id, label, version, cover_art, display_group_position
        pass

    if entity.get('available_regions'):
        print('available regions: {available_regions}'.format(**entity))

    # on tracks
    if entity.get('song'):
        song = entity.get('song')
        print('canonical_track_gid: {canonical_track_gid}'.format(**song))
        print('canonical_recording_gid: {canonical_recording_gid}'.format(**song))
        print('canonical_track_uri: {canonical_track_uri}'.format(**song))
        print('canonical_recording_uri: {canonical_recording_uri}'.format(**song))

    if entity.get('song_members'):
        print('song members:')
        for member in entity.get('song_members'):
            print('\tname: {name}, uri: {uri}'.format(**member))

    if entity.get('album'):
        album = entity.get('album')
        print('name: {name}, type: {type}, uri: {uri}'.format(**album))

    if entity.get('recording'):
        recording = entity.get('recording')
        print('uri: {uri}'.format(**recording))

    if entity.get('credits_line_artists'):
        print('credits line artists:')
        for line_artist in entity.get('credits_line_artists'):
            # type and weight are available on track, but not album
            #print('\trole: {role}, type: {type}, name: {name}, weight: {weight}, uri: {uri}'.format(**line_artist))
            print('\trole: {role}, name: {name}, uri: {uri}'.format(**line_artist))

    if entity.get('artists'):
        print('artists:')
        for artist in entity.get('artists'):
            # type and weight is available on track, but not album
            print('\trole: {role}, name: {name}, uri: {uri}'.format(**artist))

    if entity.get('recording_members'):
        print('recording_members:')
        for member in entity.get('recording_members'):
            print('\tname: {name}, uri: {uri}, position: {position}'.format(**member))

    if entity.get('cover_art'):
        pass




#

COMMANDS = [entity]

# END
