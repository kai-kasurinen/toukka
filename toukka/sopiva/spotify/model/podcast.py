#

from typing import List, Optional
from dataclasses import dataclass

from tekore.model.base import Item
from tekore.model.member import Image, Copyright
from tekore.model.album.base import ReleaseDatePrecision
from tekore.model.paging import OffsetPaging


@dataclass
class EpisodePaging(OffsetPaging):
    items: List['Episode']

    def __post_init__(self):
        # NOTE: search returns nulls
        self.items = [Episode(**episode) for episode in self.items if episode is not None]


@dataclass
class ShowPaging(OffsetPaging):
    items: List['Show']

    def __post_init__(self):
        self.items = [Show(**show) for show in self.items]


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
    episodes: Optional[EpisodePaging] = None

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
    show: Optional[Show] = None

    def __post_init__(self):
        if self.show is not None:
            self.show = Show(**self.show)
        self.release_date_precision = ReleaseDatePrecision[self.release_date_precision]


# END
