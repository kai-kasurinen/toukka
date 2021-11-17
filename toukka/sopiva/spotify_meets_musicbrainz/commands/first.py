#

from ..cli import cli_root
from ..first import print_currently_listening


@cli_root.command()
def currently_listening():
    print_currently_listening()


# END
