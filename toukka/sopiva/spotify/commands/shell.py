
import IPython

from toukka.sopiva.spotify.util import get_spotify, get_spotify_with_client_credentials
from toukka.sopiva.spotify.cli import cli_root
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_history.util import get_spotify_history


# FIXME: move to toukka
@cli_root.command()
def shell():
    spotify = get_spotify()
    spotify_history = get_spotify_history()
    IPython.embed()


# END
