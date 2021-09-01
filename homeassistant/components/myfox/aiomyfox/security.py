"""Myfox Security."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AbstractMyfoxClient
    from .typing import SecurityData, SecurityLevel


class Security:
    """Class that represents a Security object in the Myfox API."""

    def __init__(self, data: SecurityData, client: AbstractMyfoxClient, site_id: int):
        """Initialize the security object."""
        self._data = data
        self._client = client
        self._site_id = site_id

    @property
    def status(self) -> int:
        """Return the site security level."""
        return self._data["status"]

    @property
    def status_label(self) -> SecurityLevel:
        """Return the site security level label."""
        return self._data["statusLabel"]

    async def set(self, security_level: SecurityLevel) -> None:
        """Set the site security level."""
        await self._client._request(
            "post", f"site/{self._site_id}/security/set/{security_level}"
        )
