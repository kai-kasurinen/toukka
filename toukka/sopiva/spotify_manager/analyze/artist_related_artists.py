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

    def get_related_artists(artist_id):
        return [artist.id for artist in spotify.artist_related_artists(artist_id)]

    def build_related_artists_graph(root_id, max_depth=10):

        # init
        seen = set()
        graph = networkx.MultiDiGraph()

        # recursive loop function
        def do_recurse(parent_id, current_id, depth):

            if depth > max_depth:
                return

            if current_id in seen:
                return
            else:
                seen.add(current_id)

            print(f'parent: {parent_id}, current: {current_id} depth: {depth}')

            childs = get_related_artists(current_id)

            graph.add_node(current_id)

            for child_id in childs:
                graph.add_edge(current_id, child_id)

            for child_id in childs:
                do_recurse(current_id, child_id, depth+1)

        do_recurse(None, root_id, 0)
        print(f'seen: {len(seen)}')
        return graph

    def analyze_graph(graph):
        print(f'graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges')
        print(f'successors: {list(graph.successors(root_artist_id))}')
        print(f'neighbors: {list(graph.neighbors(root_artist_id))}')

    # main
    root_artist_id = get_artist_id_from_uri(artist_uri)
    related_artists_graph = build_related_artists_graph(root_artist_id)
    analyze_graph(related_artists_graph)


# END
