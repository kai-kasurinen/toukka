#

from ratelimit import limits, sleep_and_retry

#
# https://musicbrainz.org/doc/XML_Web_Service/Rate_Limiting
# 
# "The rate at which your IP address is making requests is measured.
# If that rate is too high, all your requests will be declined (http 503)
# until the rate drops again. Currently that rate is (on average) 1 request per second."
#
# not true, as 1 request per second hit ratelimiter
#
# server responses with headers:
# x-ratelimit-limit: 1200
# x-ratelimit-remaining: 867
# x-ratelimit-reset: 1536692436
#
# we need shared ratelimit to all calls to musicbrainz server
# this is a bit kludge
#
# period is seconds
@sleep_and_retry
@limits(calls=1, period=1.5)
def musicbrainz_server_ratelimit_sleeper():
    pass
