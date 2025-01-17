import json
from json import JSONDecodeError
from typing import Any, Callable, TypeAlias

from httpx import AsyncClient

from app.configs import get_logger

from .exceptions import HTTPException

Json: TypeAlias = str


class BaseApi:
    logger = get_logger()

    def __init__(self, url: str):
        self.HEADERS = {'Content-Type': 'application/json'}
        self.URL: str = url
        self._status_code: int = -1

    @staticmethod
    def _validateJson(jsondata: Callable[[], dict[str, str]]) -> dict[str, str] | None:
        try:
            return jsondata()
        except JSONDecodeError:
            return None

    def _concat_url(self, url: str) -> str:
        return self.URL + url

    async def _request(self, url: str, query_params=None, method='GET', **kwargs):
        url = self._concat_url(url)
        self.logger.debug(f'{url}, {query_params=}, {self.HEADERS=}')

        async with AsyncClient(follow_redirects=True) as client:
            self._response = await client.request(
                method=method, url=url, params=query_params, headers=self.HEADERS, **kwargs
            )

            self.status_code = self._response.status_code
            self.logger.debug(self._response.status_code)
            self.logger.debug(self._response.text)

            if self._response.status_code < 300:
                response_json = self._validateJson(self._response.json)
                if response_json:
                    return response_json
                return {'text': self._response.text}
            else:
                raise HTTPException(self._response.status_code, self._response.text)

    @property
    def status_code(self) -> int:
        return self._status_code

    @status_code.setter
    def status_code(self, value: int) -> None:
        self._status_code = value

    @staticmethod
    def serialize(data: Json) -> dict[Any, Any]:
        return json.loads(data)
