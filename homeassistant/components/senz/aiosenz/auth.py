#    Copyright 2021, Milan Meulemans
#
#    This file is part of aiosenz.
#
#    aiosenz is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    aiosenz is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with aiosenz.  If not, see <https://www.gnu.org/licenses/>.

"""SENZ OAuth2 authentication."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, cast

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from httpx import AsyncClient, Response

OAUTH2_AUTHORIZE = "https://id.senzthermostat.nvent.com/connect/authorize"
OAUTH2_TOKEN = "https://id.senzthermostat.nvent.com/connect/token"
API = "https://api.senzthermostat.nvent.com/api/v1"


class AbstractSENZAuth(ABC):
    """Abstract class to make authenticated requests to the SENZ RestAPI."""

    def __init__(self, httpx_client: AsyncClient):
        """Store the httpx AsyncClient so we can make requests."""
        self._httpx_client = httpx_client

    @abstractmethod
    async def get_access_token(self) -> str:
        """Return a valid access token."""

    async def _request(
        self, method: str, url: str, json: dict | None = None, **kwargs: dict[str, Any]
    ) -> Response:
        """Make a request to the SENZ RestAPI."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        access_token = await self.get_access_token()
        headers["authorization"] = f"Bearer {access_token}"

        resp = await self._httpx_client.request(
            method,
            f"{API}/{url}",
            headers=headers,
            json=json,
        )
        resp.raise_for_status()
        return resp


class SENZAuth(AbstractSENZAuth):
    """Class with OAuth2 token handler to make authenticated requests to the SENZ API."""

    def __init__(
        self,
        httpx_client: AsyncClient,
        client_id: str,
        client_secret: str,
        redirect_uri: str | None = None,
        token: OAuth2Token | None = None,
    ) -> None:
        """Initialize the OAuth2 client and the AbstractSENZAuth class."""
        super().__init__(httpx_client)
        self._oauth_client = AsyncOAuth2Client(
            client_id,
            client_secret,
            scope="restapi",
            redirect_uri=redirect_uri,
            token=token,
        )

    async def get_access_token(self) -> str:
        """Return a valid access token."""
        if self._oauth_client.token.is_expired():
            self._oauth_client.refresh_token(OAUTH2_TOKEN)

        return cast(str, self._oauth_client.token["access_token"])

    async def get_authorization_url(self) -> tuple[str, str]:
        """Return an authorization uri and state tuple."""
        return cast(
            tuple[str, str],
            self._oauth_client.create_authorization_url(OAUTH2_AUTHORIZE),
        )

    async def set_token_from_authorization_response(
        self, authorization_response: str
    ) -> None:
        """Set the OAuth2 token from an authorization response."""
        self._oauth_client.token = await self._oauth_client.fetch_token(
            OAUTH2_TOKEN, authorization_response=authorization_response
        )

    async def get_token(self) -> OAuth2Token:
        """Get the OAuth2 token."""
        return self._oauth_client.token

    async def close(self) -> None:
        """Close the OAuth2 client."""
        await self._oauth_client.aclose()
