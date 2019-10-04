#

#

'''experimental spotify artist commands'''

import pprint

import argh
import spotipy

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer import first as printer


'''
    results = paging.get('items')
    while paging.get('next'):
        logger.debug('getting results %s/%s', paging.get('offset'), paging.get('total'))
        paging = self.next(paging)
        results.extend(paging.get('items'))
    return results
'''

def artist_albums(uri):
    '''get artist albums'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    # FIXME: got type error with default market
    paging = spotify.artist_albums(uri_id, market='FI')

    for page in spotify.pager(paging):
        for album in page.items:
            # FIXME: on items albums are simple and printer only supports full
            # FIXME: we lose album group
            album_full = spotify.album(album.id)
            print()
            # FIXME: print oneline
            printer.print_album(album_full)

    #pprint.pprint(albums)
    #printer.print_albums(albums)


'''
    grouped = False
    if grouped:
        group_album = [a for a in albums if a.get('album_group') == 'album']
        group_single = [a for a in albums if a.get('album_group') == 'single']
        group_compilation = [a for a in albums if a.get('album_group') == 'compilation']
        group_appears_on = [a for a in albums if a.get('album_group') == 'appears_on']

    _print_albums(albums)
'''

#

COMMANDS = [
    artist_albums
    ]

# END
