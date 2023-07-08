#

import time
import asyncio
import logging

from typing import Optional, Union, Coroutine

from tekore._sender.extending import ExtendingSender
from tekore._sender.concrete import Sender, SyncSender
from tekore._sender.base import Request, Response


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RetryingSender404(ExtendingSender):
    """
    Retry requests if unsuccessful.

    On server errors the set amount of retries are used to resend requests.
    On :class:`TooManyRequests` the `Retry-After` header is checked and used
    to wait before requesting again.

    .. note::

        Even when the number of retries is set to zero,
        retries based on rate limiting are still performed.

    Parameters
    ----------
    retries
        maximum number of retries on server errors before giving up
    sender
        request sender, :class:`SyncSender` if not specified

    Examples
    --------
    Use for only rate limiting by leaving the retry count to zero.

    .. code:: python

        tk.RetryingSender()

    Pass the maximum number of retries to retry failed requests.

    .. code:: python

        tk.RetryingSender(retries=3)
    """

    def __init__(self, retries: int = 0, sender: Sender = None):
        super().__init__(sender)
        self.retries = retries

    def __repr__(self):
        contains = f'(retries={self.retries}, sender={self.sender!r})'
        return type(self).__name__ + contains

    def send(
        self, request: Request
    ) -> Union[Response, Coroutine[None, None, Response]]:
        """Delegate request to underlying sender and retry if failed."""
        if self.is_async:
            return self._async_send(request)

        tries = self.retries + 1
        delay_seconds = 1

        while tries > 0:
            r = self.sender.send(request)

            if r.status_code == 429:
                seconds = r.headers.get('Retry-After', 1)
                time.sleep(int(seconds) + 1)
            elif r.status_code >= 500 and tries > 1:
                logger.debug('code %i and retries %i', r.status_code, tries)
                tries -= 1
                time.sleep(delay_seconds)
                delay_seconds *= 2
            # NOTE: stupid spotify bug
            elif r.status_code >= 404 and tries > 1:
                logger.warning('404, retrying')
                tries -= 1
                time.sleep(delay_seconds)
                delay_seconds *= 2
            else:
                return r

    async def _async_send(self, request: Request) -> Response:
        tries = self.retries + 1
        delay_seconds = 1

        while tries > 0:
            r = await self.sender.send(request)

            if r.status_code == 429:
                seconds = r.headers.get('Retry-After', 1)
                await asyncio.sleep(int(seconds) + 1)
            elif r.status_code >= 500 and tries > 1:
                tries -= 1
                await asyncio.sleep(delay_seconds)
                delay_seconds *= 2
            else:
                return r


# END
