#

import typing

import httpx
import httpx_cache
import diskcache

# TODO: write!


class FanOutCacheAdapter(httpx_cache.cache.base.BaseCache):
    def __init__(self, *args, **kwargs):
        self.serializer = httpx_cache.serializer.common.MsgPackSerializer()
        self.data = diskcache.FanoutCache(*args, **kwargs)
        # seconds, week?
        self.default_expire = 60*60*24*7

    def _get_cache_key(self, request: httpx.Request) -> str:
        return httpx_cache.utils.get_cache_key(request)

    def _get(self, request: httpx.Request) -> typing.Optional[httpx.Response]:
        key = self._get_cache_key(request)
        cached = self.data.get(key)
        if cached is not None:
            return self.serializer.loads(cached=cached, request=request)
        return None

    def get(self, request: httpx.Request) -> typing.Optional[httpx.Response]:
        return self._get(request)

    async def aget(self, request: httpx.Request) -> typing.Optional[httpx.Response]:
        return self._get(request)

    def set(
            self,
            *,
            request: httpx.Request,
            response: httpx.Response,
            content: typing.Optional[bytes] = None,
            ) -> None:

        key = self._get_cache_key(request)
        to_cache = self.serializer.dumps(response=response, content=content)
        self.data.set(key, to_cache, expire=self.default_expire)

    async def aset(
            self,
            *,
            request: httpx.Request,
            response: httpx.Response,
            content: typing.Optional[bytes] = None,
            ) -> None:
        key = self._get_cache_key(request)
        to_cache = self.serializer.dumps(response=response, content=content)
        self.data.set(key, to_cache)

    def delete(self, request: httpx.Request) -> None:
        key = self._get_cache_key(request)
        self.data.delete(key)

    async def adelete(self, request: httpx.Request) -> None:
        key = self._get_cache_key(request)
        self.data.delete(key)


# END
