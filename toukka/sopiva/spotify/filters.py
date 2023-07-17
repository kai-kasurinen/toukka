#

import operator


# TODO: ?

def make_multi_filter(filters, func=all):
    def multi_filter(x):
        return func([f(x) for f in filters])
    return multi_filter


def make_filter_by_album_type(album_type):
    def filter_by_album_type(album):
        if album.album_type == album_type:
            return True
        else:
            return False
    return filter_by_album_type


def make_filter_by_album_label(label_name):
    def filter_by_album_label(album):
        if album.label == label_name:
            return True
        else:
            return False
    return filter_by_album_label


def make_filter_by_artist_genre(genre):
    def filter_by_artist_genre(artist):
        if genre in artist.genres:
            return True
        else:
            return False
    return filter_by_artist_genre


# NOTE: chatgpt example
def make_filter_by_attribute(attribute, value):
    def filter_by_attribute(obj):
        if hasattr(obj, attribute) and getattr(obj, attribute) == value:
            return True
        else:
            return False
    return filter_by_attribute


# NOTE: chatgpt example
# popular_artists = filter_objects_by_attribute(artists, 'popularity', 50, operator.gt)
#
def filter_objects_by_attribute(objects, attribute, value, op=operator.eq):
    return filter(lambda obj: op(getattr(obj, attribute), value), objects)
