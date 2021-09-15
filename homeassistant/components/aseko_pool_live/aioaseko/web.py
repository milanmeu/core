"""aioAseko web api."""
from __future__ import annotations

import logging

from aiohttp import ClientError, ClientResponse, ClientSession

from .exceptions import APIUnavailable, InvalidAuthCredentials
from .unit import Unit

_LOGGER = logging.getLogger(__name__)


class WebAccount:
    """Aseko web account."""

    def __init__(self, session: ClientSession, username: str, password: str) -> None:
        """Init Aseko account."""
        self._session = session
        self._username = username
        self._password = password

    async def _request(
        self, method: str, path: str, data: dict | None = None
    ) -> ClientResponse:
        """Make a request to the Aseko API."""
        resp = await self._session.request(
            method, f"https://pool.aseko.com/api/{path}", data=data
        )
        if resp.status == 401:
            raise InvalidAuthCredentials
        _LOGGER.warning(await resp.json())
        try:
            resp.raise_for_status()
        except ClientError:
            raise APIUnavailable
        return resp

    async def login(self) -> AccountInfo:
        """Login to the Aseko web API."""
        resp = await self._request(
            "post",
            "login",
            {
                "username": self._username,
                "password": self._password,
                "agree": "on",
            },
        )
        data = await resp.json()
        return AccountInfo(data["email"], data["userId"], data["language"])

    async def get_devices(self) -> list[Unit]:
        """Get units."""
        resp = await self._request("get", "units")
        data = await resp.json()
        return [
            Unit(
                self,
                int(item["serialNumber"]),
                item["type"],
                item["name"],
                item["notes"],
                item["timezone"],
                item["isOnline"],
                item["dateLastData"],
                item["hasError"],
            )
            for item in data["items"]
        ]


class AccountInfo:
    """Aseko account info."""

    def __init__(
        self,
        email: str,
        user_id: str,
        language: str,
    ) -> None:
        """Init Aseko account info."""
        self._email = email
        self._user_id = user_id
        self._language = language

    @property
    def email(self) -> str:
        """Return email."""
        return self._email

    @property
    def user_id(self) -> str:
        """Return user id."""
        return self._user_id

    @property
    def language(self) -> str:
        """Return language."""
        return self._language
