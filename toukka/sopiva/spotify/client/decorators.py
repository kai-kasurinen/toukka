#

from typing import Generator, Tuple, Optional

import logging
import textwrap

from boltons.funcutils import wraps


logger = logging.getLogger(__name__)


def alter_limit(f, limit=None):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'limit' in kwargs.keys():
            return f(*args, **kwargs)
        else:
            return f(*args, **kwargs, limit=limit)
    return wrapper


def alter_description(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'description' in kwargs.keys():
            if kwargs['description'] is not None:
                description = kwargs['description']
                description_len = len(description)
                description_len_raw = len(description.encode('utf-8'))

                if description_len_raw > 300:

                    logger.warning(
                        'playlist description is too long (%i, %i), shortening it',
                        description_len, description_len_raw)

                    shorted = textwrap.shorten(description, 298, placeholder='...')
                    shorted_len = len(shorted)
                    shorted_len_raw = len(shorted.encode('utf-8'))

                    kwargs['description'] = shorted

                    # TODO: remove
                    if shorted_len_raw > 300:
                        logger.warning(
                            'shorted description length: %i, %i',
                            shorted_len, shorted_len_raw)
                        logger.warning(shorted)

        return f(*args, **kwargs)
    return wrapper


def check_from_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # TODO: remove
        if kwargs.get('market') == 'from_token':
            raise Exception('market is from_token')
        #elif 'market' not in kwargs.keys():
        #    raise Exception('market is not defined')
        else:
            return f(*args, **kwargs)
    return wrapper
