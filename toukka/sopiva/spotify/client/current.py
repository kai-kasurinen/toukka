#


from .extented import SpotifyExtended
from .cached import SpotifyCached
# from .podcast import SpotifyPodcast


class Spotify(SpotifyExtended, SpotifyCached):
    pass


# END
