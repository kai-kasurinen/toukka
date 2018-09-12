#

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# TODO:
# https://stackoverflow.com/questions/20247354/limiting-throttling-the-rate-of-http-requests-in-grequests
# https://github.com/se7entyse7en/requests-throttler
# http://william.holroyd.name/2014/11/02/how-do-most-apis-handle-rate-limiting/
#
# headers:
# x-ratelimit-limit: 1200
# x-ratelimit-remaining: 810
# x-ratelimit-reset: 1536601269

