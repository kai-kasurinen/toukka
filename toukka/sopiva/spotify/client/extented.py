#

from typing import Generator, Tuple, Optional

import functools

from tekore.client import Spotify
from tekore.model.paging import Paging
from tekore.model.base import Item

import tekore.convert

from requests import HTTPError


def alter_limit(f, limit=None):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'limit' in kwargs.keys():
            return f(*args, **kwargs)
        else:
            return f(*args, **kwargs, limit=limit)
    return wrapper


def catch_404(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            ret = f(*args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise
        else:
            return ret
    return wrapper


class SpotifyExtended(Spotify):

    # update limits
    #
    # album
    album_tracks = alter_limit(Spotify.album_tracks, limit=50)
    # artist
    artist_albums = alter_limit(Spotify.artist_albums, limit=50)
    # search
    search = alter_limit(Spotify.search, limit=50)
    # library
    saved_albums = alter_limit(Spotify.saved_albums, limit=50)
    saved_tracks = alter_limit(Spotify.saved_tracks, limit=50)
    # player
    playback_recently_played = alter_limit(Spotify.playback_recently_played, limit=50)
    # browse
    featured_playlists = alter_limit(Spotify.featured_playlists, limit=50)
    new_releases = alter_limit(Spotify.new_releases, limit=50)
    categories = alter_limit(Spotify.categories, limit=50)
    category_playlists = alter_limit(Spotify.category_playlists, limit=50)
    recommendations = alter_limit(Spotify.recommendations, limit=100)
    # personalition
    current_user_top_artists = alter_limit(Spotify.current_user_top_artists, limit=50)
    current_user_top_tracks = alter_limit(Spotify.current_user_top_tracks, limit=50)
    # follow
    followed_artists = alter_limit(Spotify.followed_artists, limit=50)
    # playlist
    followed_playlists = alter_limit(Spotify.followed_playlists, limit=50)
    playlists = alter_limit(Spotify.playlists, limit=50)

    # https://github.com/felix-hilden/tekore/issues/145
    # catch 404
    next = catch_404(Spotify.next)

    def _sync_all_pages(self, page: Paging):
        yield page
        while page.next is not None:
            page = self.next(page)
            if page is None:
                return
            yield page

    #
    def uri_to_item(self, uri: str) -> Item:
        uri_type, uri_id = tekore.convert.from_uri(uri)
        if uri_type == 'artist':
            return self.artist(uri_id)
        elif uri_type == 'album':
            return self.album(uri_id)
        elif uri_type == 'track':
            return self.track(uri_id)
        elif uri_type == 'playlist':
            return self.playlist(uri_id)
        else:
            raise Exception(f'unsupported uri: {uri} ({uri_type}, {uri_id})')

    @property
    def convert(self):
        return tekore.convert

    # FIXME: move?
    def convert_from_uri(self, uri: str) -> Tuple:
        return tekore.convert.from_uri(uri)

# END
