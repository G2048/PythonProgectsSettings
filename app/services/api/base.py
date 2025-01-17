import json
from json import JSONDecodeError
from typing import TypeAlias

from httpx import AsyncClient

from app.configs import get_logger

from .exceptions import HTTPException

Json: TypeAlias = str


class BaseApi:
    logger = get_logger()

    def __init__(self, url):
        self.HEADERS = {'Content-Type': 'application/json'}
        self.URL = url
        self._status_code = None

    @staticmethod
    def _validateJson(jsondata):
        try:
            return jsondata()
        except JSONDecodeError:
            return None

    async def _request(self, url, query_params=None, method='GET', **kwargs):
        self.URL += url
        self.logger.debug(f'{url}, {query_params=}, {self.HEADERS=}')

        async with AsyncClient(follow_redirects=True) as client:
            self._response = await client.request(
                method=method, url=self.URL, params=query_params, headers=self.HEADERS, **kwargs
            )

            self.status_code = self._response.status_code
            self.logger.debug(self._response.status_code)
            self.logger.debug(self._response.text)

            if self._response.status_code >= 500:
                raise HTTPException(self._response.status_code, self._response.text)

            if self._response.status_code < 300:
                response_json = self._validateJson(self._response.json)
                if response_json:
                    return response_json

            return {'text': self._response.text}

    @property
    def status_code(self) -> int | None:
        return self._status_code

    @status_code.setter
    def status_code(self, value) -> None:
        self._status_code = value

    @staticmethod
    def serialize(data: Json) -> dict:
        return json.loads(data)
