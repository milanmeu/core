"""Myfox groups."""
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from .devices import Shutter, Socket

if TYPE_CHECKING:
    from .client import AbstractMyfoxClient
    from .typing import ElectricalGroupData, GroupData, ShutterGroupData


class Group(ABC):
    """Class that represents an abstract group in the Myfox API."""

    def __init__(self, data: GroupData, client: AbstractMyfoxClient, site_id: int):
        """Initialize the GroupShutter object."""
        self._data = data
        self._client = client
        self._site_id = site_id

    @property
    def group_id(self) -> int:
        """Return the group identifier."""
        return self._data["groupId"]

    @property
    def label(self) -> str:
        """Return the group label."""
        return self._data["label"]

    @property
    def type(self) -> str:
        """Return the group type."""
        return self._data["type"]


class ElectricGroup(Group):
    """Class that represents a group of type electric in the Myfox API."""

    _data: ElectricalGroupData

    def __init__(
        self, data: ElectricalGroupData, client: AbstractMyfoxClient, site_id: int
    ):
        """Initialize the GroupElectric object."""
        super().__init__(data, client, site_id)

    @property
    def devices(self) -> list[Socket]:
        """Return list of devices in group."""
        return [
            Socket(socket_data, self._client, self._site_id)
            for socket_data in self._data["devices"]
        ]

    async def off(self) -> None:
        """Turn off all electric devices from a group."""
        await self._client._request(
            "post", f"site/{self._site_id}/group/{self.group_id}/electric/off"
        )

    async def on(self) -> None:
        """Turn on all electric devices from a group."""
        await self._client._request(
            "post", f"site/{self._site_id}/group/{self.group_id}/electric/on"
        )


class ShutterGroup(Group):
    """Class that represents a group of type shutter in the Myfox API."""

    _data: ShutterGroupData

    def __init__(
        self, data: ShutterGroupData, client: AbstractMyfoxClient, site_id: int
    ):
        """Initialize the ShutterGroup object."""
        super().__init__(data, client, site_id)

    @property
    def devices(self) -> list[Shutter]:
        """Return list of devices in group."""
        return [
            Shutter(shutter_data, self._client, self._site_id)
            for shutter_data in self._data["devices"]
        ]

    async def close(self) -> None:
        """Close all shutters from a group."""
        await self._client._request(
            "post", f"site/{self._site_id}/group/{self.group_id}/shutter/close"
        )

    async def open(self) -> None:
        """Open all shutters from a group."""
        await self._client._request(
            "post", f"site/{self._site_id}/group/{self.group_id}/shutter/open"
        )
