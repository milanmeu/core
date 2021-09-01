"""Myfox Client."""
from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import Any, cast

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from httpx import AsyncClient, Response

from .site import Site

logger = logging.getLogger(__name__)

OAUTH2_AUTHORIZE = "https://api.myfox.me/oauth2/authorize"
OAUTH2_TOKEN = "https://api.myfox.me/oauth2/token"
API = "https://api.myfox.me/v2"


class AbstractMyfoxClient(ABC):
    """Myfox API Client."""

    def __init__(self, httpx_client: AsyncClient):
        """Abstract class to make authenticated requests. Initialize the API CLient and store the auth so we can make requests."""
        self._httpx_client = httpx_client

    async def get_sites(self) -> list[Site]:
        """Return the sites."""
        resp = await self._request("get", "client/site/items")
        return [
            Site(site_data, self) for site_data in (resp.json())["payload"]["items"]
        ]

    @abstractmethod
    async def get_access_token(self) -> str:
        """Return a valid access token."""

    async def _request(
        self, method: str, url: str, **kwargs: dict[str, Any]
    ) -> Response:
        """Make a request to the Myfox API."""
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
        )
        resp.raise_for_status()
        logger.warning(resp.text)
        return resp


class MyfoxClient(AbstractMyfoxClient):
    """Abstract class to make authenticated requests."""

    def __init__(
        self,
        httpx_client: AsyncClient,
        client_id: str,
        client_secret: str,
        redirect_uri: str | None = None,
        token: OAuth2Token | None = None,
    ) -> None:
        """Initialize the auth."""
        super().__init__(httpx_client)
        self._oauth_client = AsyncOAuth2Client(
            client_id, client_secret, redirect_uri=redirect_uri, token=token
        )

    async def get_authorization_url(self) -> tuple[str, str]:
        """Return an authorization uri and state tuple."""
        return cast(
            tuple[str, str],
            self._oauth_client.create_authorization_url(OAUTH2_AUTHORIZE),
        )

    async def set_token_from_authorization_response(
        self, authorization_response: str
    ) -> OAuth2Token:
        """Set the token from an authorization response."""
        self._oauth_client.token = await self._oauth_client.fetch_token(
            OAUTH2_TOKEN, authorization_response=authorization_response
        )

    async def get_access_token(self) -> str:
        """Return a valid access token."""
        if self._oauth_client.token.is_expired():
            self._oauth_client.refresh_token(OAUTH2_TOKEN)

        return cast(str, self._oauth_client.token["access_token"])

    async def close(self) -> None:
        """Close the AsyncOAuth2Client."""
        await self._oauth_client.aclose()
