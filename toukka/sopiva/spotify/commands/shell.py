
import IPython

from toukka.sopiva.spotify.util import get_spotify, get_spotify_with_client_credentials
from toukka.sopiva.spotify.cli import cli_root
from toukka.sopiva.spotify.printer.first import printer


# FIXME: move to toukka
@cli_root.command()
def shell():
    IPython.embed()


# END
