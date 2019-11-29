#


from .extented import SpotifyExtended
from .cached import SpotifyCached
# from .cached_mongo import SpotifyMongo


class Spotify(SpotifyExtended, SpotifyCached):
    pass


# END
