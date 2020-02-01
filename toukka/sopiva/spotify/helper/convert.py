#

from functools import singledispatchmethod

from spotipy.model.track import FullTrack, SimpleTrack
from spotipy.model.artist import FullArtist, SimpleArtist
from spotipy.model.album import SimpleAlbum
from spotipy.model.album.full import FullAlbum


from .base import HelperBase


class HelperConvert(HelperBase):

    @singledispatchmethod
    def to_full(
            self,
            item,
            ):
        raise NotImplementedError('not yet supported type: %s' % type(item))

    @to_full.register
    def simple_artist_to_full(
            self,
            item: SimpleArtist
            ):
        return self.spotify.artist(item.id)

    @to_full.register
    def simple_album_to_full(
            self,
            item: SimpleAlbum
            ):
        return self.spotify.album(item.id)

    @to_full.register
    def simple_track_to_full(
            self,
            item: SimpleTrack
            ):
        return self.spotify.track(item.id)

    @to_full.register
    def list_to_full(
            self,
            item: list
            ):
        return [self.to_full(x.id) for x in item]


# END
