#

import logging
import wikidata
import urllib.error

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _iterlists(entity):
    ''' same as entity.iterlists with exception handling '''
    for prop in entity:
        try:
            v = entity.getlist(prop)
        except wikidata.datavalue.DatavalueError as error:
            logger.error('%s: %s', prop, error)
        except KeyError as error:
            logger.error('%s: %s', prop, error)
        yield prop, v


def print_entity(entity):
    print()
    _print_entity_oneline(entity)
    _print_entity_all_props(entity)


def _print_entity_oneline(entity):
    print('{}: {} ({})'.format(entity.id, entity.label, entity.description))


def _print_entity_multiline(entity):
    print('label: {}'.format(entity.label))
    print('id: {}'.format(entity.id))
    print('description: {}'.format(entity.description))


def _print_entity_all_props(entity):
    key_value_lists = _iterlists(entity)

    for key, values in key_value_lists:
        values_to_print = list()
        for value in values:
            if isinstance(value, wikidata.entity.Entity):
                value = _load_entity(value)
                # not found
                if value is None:
                    continue
                values_to_print.append(value.label)
            else:
                values_to_print.append(value)
        if len(values_to_print) == 1:
           values_to_print  = values_to_print[0]
        print('\t{}: {}'.format(key.label, values_to_print))


def _load_entity(entity):
    try:
        entity.load()
    except urllib.error.HTTPError as error:
        if error.getcode() == 404:
            logger.error('load entity: %s not found', entity.id)
            entity = None
        else:
            raise
    return entity
