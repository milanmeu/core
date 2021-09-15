"""aioAseko account."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiohttp import ClientError

from .exceptions import APIUnavailable, InvalidAuthCredentials
from .unit import Unit

if TYPE_CHECKING:
    from aiohttp import ClientResponse, ClientSession

_LOGGER = logging.getLogger(__name__)


class MobileAccount:
    """Aseko account."""

    def __init__(
        self,
        session: ClientSession,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
    ) -> None:
        """Init Aseko account."""
        self._session = session
        self._username = username
        self._password = password
        self._access_token = access_token

    @property
    def access_token(self) -> str | None:
        """Return access token."""
        return self._access_token

    async def _request(
        self, method: str, path: str, data: dict | None = None
    ) -> ClientResponse:
        """Make a request to the Aseko API."""
        resp = await self._session.request(
            method,
            f"https://pool.aseko.com/api/v1/{path}",
            data=data,
            headers=None
            if self._access_token is None
            else {"access-token": self.access_token},
        )
        _LOGGER.warning(await resp.json())
        if resp.status == 401:
            raise InvalidAuthCredentials
        try:
            resp.raise_for_status()
        except ClientError:
            raise APIUnavailable
        return resp

    async def login(self) -> None:
        """Login to Aseko Pool Live with username and password."""
        resp = await self._request(
            "post",
            "login",
            {
                "username": self._username,
                "password": self._password,
                "firebaseId": "",
            },
        )
        data = await resp.json()
        self._access_token = data["accessToken"]

    async def logout(self) -> None:
        """Logout Aseko Pool Live account."""
        await self._request("post", "v1/logout")

    async def get_devices(self) -> list[Unit]:
        """Get units."""
        resp = await self._request("get", "units")
        data = await resp.json()
        return [
            Unit(
                self,
                int(item["serialNumber"]),
                item["type"],
                item.get("name"),
                item.get("notes"),
                item["timezone"],
                item["isOnline"],
                item["dateLastData"],
                item["hasError"],
            )
            for item in data["items"]
        ]
