#


from .extented import SpotifyExtended
from .cached import SpotifyCached
from .episode import SpotifyEpisode


class Spotify(SpotifyExtended, SpotifyEpisode, SpotifyCached):
    pass


# END
