#

import logging
import pycountry

from toukka.itunes.itunes import iTunes
from beanbag import BeanBagException

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)


invalid_stores = []
music_not_available_stores = []

# 20181220
# invalid_stores = ['AW', 'AF', 'AX', 'AD', 'AS', 'AQ', 'TF', 'BI', 'BQ', 'BA', 'BL', 'BV', 'CF', 'CC', 'CD', 'CK', 'KM', 'CU', 'CW', 'CX', 'DJ', 'ER', 'EH', 'FK', 'FO', 'GA', 'GE', 'GG', 'GI', 'GN', 'GP', 'GQ', 'GL', 'GF', 'GU', 'HM', 'HT', 'IM', 'IO', 'IR', 'IQ', 'JE', 'KI', 'LS', 'MF', 'MA', 'MC', 'MH', 'ME', 'MP', 'MQ', 'YT', 'NC', 'NF', 'NU', 'NR', 'PN', 'PR', 'KP', 'PF', 'RE', 'RW', 'SD', 'GS', 'SH', 'SJ', 'SM', 'SO', 'PM', 'SS', 'SX', 'SY', 'TG', 'TK', 'TL', 'TO', 'TV', 'UM', 'VA', 'VI', 'VU', 'WF', 'WS', 'ZM']

# 20181220
# music_not_available_stores =  ['AO', 'AL', 'BJ', 'BD', 'BT', 'CN', 'CI', 'CM', 'CG', 'DZ', 'ET', 'GY', 'HR', 'IS', 'JM', 'KW', 'LR', 'LY', 'LC', 'LI', 'MG', 'MV', 'MK', 'ML', 'MM', 'MR', 'MS', 'MW', 'PK', 'PW', 'PS', 'SN', 'SB', 'SL', 'RS', 'ST', 'SR', 'SC', 'TC', 'TD', 'TN', 'TZ', 'UY', 'VC', 'YE']

def lookup_id_from_all_countries(id):
    itunes = iTunes()

    found_country = []
    not_found_country = []
    invalid_country = []
    failed_country = []
    found = []

    logger.debug('looking all country stores...')
    for country in pycountry.countries:
        logger.debug('%s (%s)', country.alpha_2, country.name)

        if country.alpha_2 in invalid_stores:
            logger.debug('skipping %s (invalid store)', country.name)
            continue

        if country.alpha_2 in music_not_available_stores:
            logger.debug('skipping %s (music not available)', country.name)
            continue

        try:
            lookup = itunes.lookup(id=id, country=country.alpha_2)
        except BeanBagException:
            logger.debug('%s failed', country.alpha_2)
            failed_country.append(country)
            continue

        result_count = lookup.get('resultCount')

        logger.debug('%s: %s' % (country, result_count))

        if result_count == 0:
            logger.debug("%s: not found", country.alpha_2)
            not_found_country.append(country)
        elif result_count == 1:
            logger.debug("%s: found", country.alpha_2)
            found_country.append(country)
        else:
            raise Exception

    print('')
    print('Found:', _get_nice_string_from_countries2(found_country))
    print('Not Found:', _get_nice_string_from_countries2(not_found_country))
    print('Failed:', _get_nice_string_from_countries2(failed_country))


def _get_nice_string_from_countries2(list_or_iterator):
    return '[' + ', '.join('%s' % (x.alpha_2) for x in list_or_iterator) + ']'


def _get_nice_string_from_countries1(list_or_iterator):
    return '[' + ', '.join('%s (%s)' % (x.name, x.alpha_2) for x in list_or_iterator) + ']'


