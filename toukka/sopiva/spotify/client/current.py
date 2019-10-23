#


from .extented import SpotifyExtended
from .cached import SpotifyCached


class Spotify(SpotifyExtended, SpotifyCached):
    pass


# END
