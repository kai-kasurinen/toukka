#

import toukka.config


def get_database_uri_from_config():
    return toukka.config.lazy_config['spotify_database']['database_uri'].get()


# END
