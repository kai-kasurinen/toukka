#


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


def make_filter_by_artist_genre(genre):
    def filter_by_artist_genre(artist):
        if genre in artist.genres:
            return True
        else:
            return False
    return filter_by_artist_genre

