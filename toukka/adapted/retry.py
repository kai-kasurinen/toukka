#

from urllib3.util.retry import Retry, log


class RetryA(Retry):

    def get_retry_after(self, response):
        retry_after = super().get_retry_after(response)
        log.debug('Retry-After: %s', retry_after)

        # https://github.com/plamere/spotipy/pull/391
        # Spotify convert from millis to seconds and then floor it to give the retry-after time.
        # This leads to multiple retrys sometimes when using their retry-after time.
        # This adds a second so that that shouldn't happen.
        if retry_after is not None:
            retry_after = retry_after + 1

        return retry_after

# END
