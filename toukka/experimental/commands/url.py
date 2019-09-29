#

import pprint
from urlobject import URLObject
from toukka.resource import ResourceURL


def parse_url(url_string):
    resource = ResourceURL(url_string)
    print(resource)
    print(resource.url)
    print(resource.service)
    print(resource.entity_type)
    print(resource.entity_id)


#

COMMANDS = [parse_url]

# END
