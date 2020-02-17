#


from .extented import SpotifyExtended
from .cached import SpotifyCached
from .podcast import SpotifyPodcast
# from .cached_mongo import SpotifyMongo


# class Spotify(SpotifyExtended, SpotifyCached):
#    pass


class Spotify(SpotifyExtended, SpotifyPodcast):
    pass


# END
