#

# TODO: use networkx - https://github.com/networkx/networkx


import collections

from toukka.sopiva.spotify.util import get_spotify


def artist_related_artists_test(artist_uri):
    spotify = get_spotify()

    artist_type, artist_id = spotify.convert.from_uri(artist_uri)

    seen = set()

    def get_related_artists(artist_id):
        return [artist.id for artist in spotify.artist_related_artists(artist_id)]

    def do_recurse(parent_id, current_id, depth=0, max_depth=5):
        if depth > max_depth:
            return

        if current_id in seen:
            return
        else:
            seen.add(current_id)

        print(f'parent: {parent_id}, current: {current_id} depth: {depth}')

        childs = get_related_artists(current_id)

        for child_id in childs:
            do_recurse(current_id, child_id, depth=depth+1)

    do_recurse(None, artist_id)
    print(f'seen: {len(seen)}')


# END
