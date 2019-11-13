#

from typing import List
from dataclasses import dataclass
from spotipy.model.base import Item
from spotipy.model.member import Image, Copyright
from spotipy.model.album.base import ReleaseDatePrecision
from spotipy.model.paging import OffsetPaging
from spotipy.client.base import SpotifyBase


@dataclass
class EpisodePaging(OffsetPaging):
    items: List[Item]  # List[Episode]

    def __post_init__(self):
        self.items = [Episode(**episode) for episode in self.items]


@dataclass
class Show(Item):
    available_markets: List[str]
    copyrights: List[Copyright]
    description: str
    explicit: bool
    external_urls: dict
    images: List[Image]
    is_externally_hosted: bool
    languages: List[str]
    media_type: str
    name: str
    publisher: str
    episodes: EpisodePaging = None

    def __post_init__(self):
        self.copyrights = [Copyright(**c) for c in self.copyrights]
        self.images = [Image(**i) for i in self.images]
        if self.episodes is not None:
            self.episodes = EpisodePaging(**self.episodes)


@dataclass
class Episode(Item):
    audio_preview_url: str
    description: str
    duration_ms: int
    explicit: bool
    external_urls: dict
    images: List[Image]
    is_externally_hosted: bool
    is_playable: bool
    language: str
    languages: List[str]
    name: str
    release_date: str
    release_date_precision: ReleaseDatePrecision
    show: Show = None

    def __post_init__(self):
        if self.show is not None:
            self.show = Show(**self.show)
        self.release_date_precision = ReleaseDatePrecision[self.release_date_precision]


class SpotifyPodcast(SpotifyBase):

    def episode(
            self,
            episode_id: str,
            market: str
    ) -> Episode:
        json = self._get('episodes/' + episode_id, market=market)
        return Episode(**json)

    def show(
            self,
            show_id: str,
            market: str
    ) -> Show:
        json = self._get('shows/' + show_id, market=market)
        return Show(**json)


# END
