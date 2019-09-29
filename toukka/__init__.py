#

# FIXME: move
__version_info__ = 0, 0, 0
__version__ = '0.0.0'
__prog_name__ = 'toukka'

## FIXME: remove
#import sys
#import os
## FIXME: hack
#sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'external'))

# FIXME: remove
from .hub.lazy import Toukka
from .resource import ResourceURL, ResourceURI

# END
