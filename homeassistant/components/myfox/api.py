"""API for Myfox bound to Home Assistant OAuth."""
from typing import cast

from httpx import AsyncClient

from homeassistant.helpers import config_entry_oauth2_flow

from .aiomyfox import AbstractMyfoxClient


class ConfigEntryMyfoxClient(AbstractMyfoxClient):
    """Provide Myfox client with authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        httpx_async_client: AsyncClient,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize Myfox auth."""
        super().__init__(httpx_async_client)
        self._oauth_session = oauth_session

    async def get_access_token(self) -> str:
        """Return a valid access token."""
        await self._oauth_session.async_ensure_token_valid()
        return cast(str, self._oauth_session.token["access_token"])
