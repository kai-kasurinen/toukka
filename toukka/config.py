#
#
# NOTE: default path ~/.config/toukka/config.yaml



import confuse

lazy_config = confuse.LazyConfig('toukka', __name__)


def print_configuration(library=None, directory=None):
    print('configuration directory is', lazy_config.config_dir())
    print(lazy_config.flatten())


COMMANDS = [print_configuration]


# END
