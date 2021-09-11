#


from tekore._sender import Sender, Request, Response

import requests

# BUG: fails with newer tekore: 400: Missing payload
# ... cos https://github.com/felix-hilden/tekore/commit/11d72683cc11b4ce275703dfb4059938bac49b51


def try_parse_json(response):
    try:
        return response.json()
    except ValueError:
        return None


class RequestsSender(Sender):

    def __init__(self, session: requests.Session = None):
        # https://github.com/psf/requests/issues/3070
        self.requests_kwargs = {'timeout': 10.0}
        self.session = session or requests.Session()

    def send(self, request: Request) -> Response:
        response = self.session.request(
            method=request.method,
            url=request.url,
            params=request.params,
            headers=request.headers,
            data=request.data,
            **self.requests_kwargs
        )
        return Response(
            url=str(response.url),
            headers=response.headers,
            status_code=response.status_code,
            content=try_parse_json(response),
        )

    def __del__(self):
        self.session.close()

    def close(self):
        self.session.close()

    @property
    def is_async(self) -> bool:
        return False
