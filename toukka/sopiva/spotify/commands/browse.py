#

from toukka.sopiva.spotify.util import get_spotify


def categories(country: str = None,
               locale: str = None):
    '''list categories'''
    spotify = get_spotify()
    paging = spotify.categories(country=country, locale=locale, limit=50)
    print(f'found {paging.total} categories')
    # FIXME: TypeError if we really get more than one page
    # 'cos "response body contains an object with a categories field"
    categories = spotify.all_items_from_paging(paging)
    for category in categories:
        print(f'{category.id:20}: {category.name}')


def featured_playlists(country: str = None,
                       locale: str = None,
                       timestamp: str = None):
    '''list categories'''
    spotify = get_spotify()
    message, paging = spotify.featured_playlists(
        country=country,
        locale=locale,
        timestamp=timestamp,
        limit=50)
    print(f'message: {message}')
    print(f'found {paging.total} featured playlists')
    playlists = spotify.all_items_from_paging(paging)
    for playlist in playlists:
        print(f'{playlist.id}: {playlist.name}')


def recommendation_genre_seeds():
    '''get list of available genre seeds'''
    return get_spotify().recommendation_genre_seeds()


#

COMMANDS = [
    categories,
    featured_playlists,
    recommendation_genre_seeds
]

# END
