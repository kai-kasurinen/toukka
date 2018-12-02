#

import logging
import wikidata

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def print_entity(entity):
    print()
    print('{}: {} ({})'.format(entity.id, entity.label, entity.description))
    #print('label: {}'.format(entity.label))
    #print('id: {}'.format(entity.id))
    #print('description: {}'.format(entity.description))

    key_value_lists = None

    try:
        key_value_lists = entity.lists()
    # https://github.com/dahlia/wikidata/issues/6
    except wikidata.datavalue.DatavalueError as error:
        logger.error(error)

    if key_value_lists is None:
        return

    for key, values in key_value_lists:
        values_to_print = list()
        for value in values:
            if isinstance(value, wikidata.entity.Entity):
                values_to_print.append(value.label)
            else:
                values_to_print.append(value)
        if len(values_to_print) == 1:
           values_to_print  = values_to_print[0]
        print('\t{}: {}'.format(key.label, values_to_print))
