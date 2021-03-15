#

# TODO: use networkx - https://github.com/networkx/networkx


import collections
import networkx

from toukka.sopiva.spotify.util import get_spotify


def artist_related_artists_test(artist_uri):
    spotify = get_spotify()

    def get_artist_id_from_uri(artist_uri):
        artist_type, artist_id = spotify.convert.from_uri(artist_uri)
        return artist_id

    def analyze_graph(graph):
        print(networkx.info(graph))

    # main
    root_artist_id = get_artist_id_from_uri(artist_uri)
    related_artists_graph = build_related_artists_graph(root_artist_id)
    analyze_graph(related_artists_graph)


def build_related_artists_graph(root_id, max_depth=5):

    # init
    spotify = get_spotify()
    seen = set()
    seen_childs = set()
    graph = networkx.DiGraph()

    def get_related_artists(artist_id):
        return [artist.id for artist in spotify.artist_related_artists(artist_id)]

    def add_artist_node(artist_id):
        artist = spotify.artist(artist_id)
        # NOTE: pydot.to_pydot confuses name
        graph.add_node(artist.id, name=artist.name)

    # recursive loop function
    def do_recurse(parent_id, current_id, depth):

        if depth > max_depth:
            return

        if current_id in seen:
            return
        else:
            seen.add(current_id)

        print(f'parent: {parent_id}, current: {current_id} depth: {depth}')

        add_artist_node(current_id)
        childs = get_related_artists(current_id)

        for child_id in childs:
            seen_childs.add(child_id)
            # If some edges connect nodes not yet in the graph, the nodes are added automatically.
            # There are no errors when adding nodes or edges that already exist.
            graph.add_edge(current_id, child_id)

        for child_id in childs:
            do_recurse(current_id, child_id, depth+1)

    do_recurse(None, root_id, 0)
    print(f'seen: {len(seen)}')
    print(f'seen childs: {len(seen_childs)}')
    return graph

# END
