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
# we need shared ratelimit to all calls to musicbrainz server
# this is a bit kludge
#
# python-musicbrainzngs has nice class:
# https://github.com/alastair/python-musicbrainzngs/blob/master/musicbrainzngs/musicbrainz.py#L352
#
# period is seconds
@sleep_and_retry
@limits(calls=1, period=1.3)
def musicbrainz_server_ratelimit_sleeper():
    pass

# search.musicbrainz.org response:
'''
HTTP/2 200 
date: Wed, 12 Sep 2018 05:49:21 GMT
content-type: application/json; charset=UTF-8
vary: Accept-Encoding
last-modified: Wed, 12 Sep 2018 04:49:18 GMT
server: Jetty(9.3.10.v20160621)
'''

'''
HTTP/2 503 
server: openresty
date: Wed, 12 Sep 2018 05:49:21 GMT
content-type: text/html
content-length: 505
etag: "58025bc0-1f9"
'''

# lets try this
# and not working
@sleep_and_retry
@limits(calls=1, period=1.3)
def musicbrainz_search_server_ratelimit_sleeper():
    pass

# END
