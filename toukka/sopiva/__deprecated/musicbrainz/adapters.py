#

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# TODO:
# https://community.metabrainz.org/t/what-do-the-x-ratelimit-headers-mean-and-how-should-they-be-used/259737
# https://stackoverflow.com/questions/20247354/limiting-throttling-the-rate-of-http-requests-in-grequests
# https://github.com/se7entyse7en/requests-throttler
# http://william.holroyd.name/2014/11/02/how-do-most-apis-handle-rate-limiting/
#
# headers:
# x-ratelimit-limit: 1200
# x-ratelimit-remaining: 810
# x-ratelimit-reset: 1536601269

'''
HTTP/2 400 
date: Wed, 12 Sep 2018 04:23:02 GMT
content-type: application/json; charset=utf-8
content-length: 93
x-ratelimit-limit: 1200
x-ratelimit-remaining: 1024
x-ratelimit-reset: 1536726183
server: Plack::Handler::Starlet
etag: "02dc195d9e42ce67054c2a0e682cacb4"
access-control-allow-origin: *

HTTP/2 503 
server: openresty
date: Wed, 12 Sep 2018 04:23:03 GMT
content-type: application/json
retry-after: 5
x-ratelimit-zone: per-ip
x-mb-rate-limiter: lua
'''

# END
