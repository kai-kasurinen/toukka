#

class MusicBrainzException(Exception):
    __slots__ = ('msg', 'response')

    def __init__(self, response, msg):
        self.msg = msg
        self.response = response

    def __repr__(self):
        return "%s(%s,%r)" % (self.__class__.__name__, self.msg, self.response)

    def __str__(self):
        msg = self.msg
        if self.response and hasattr(self.response, "content"):
            msg = "%s - response: %s" % (self.msg, self.response.content)
        return msg


class MusicBrainzRateLimitException(MusicBrainzException):
    pass


class HTTPErrorFake(MusicBrainzException):
    __slots__ = ('msg', 'response', 'code')

    def __init__(self, response, msg):
        self.msg = msg
        self.response = response
        self.code = self.response.status_code
