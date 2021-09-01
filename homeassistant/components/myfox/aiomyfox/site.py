"""Myfox site."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .devices import Shutter, Socket
from .groups import ElectricGroup, ShutterGroup
from .security import Security

if TYPE_CHECKING:
    from .client import AbstractMyfoxClient
    from .typing import SiteData


class Site:
    """Class that represents a Site object in the Myfox API."""

    def __init__(self, data: SiteData, client: AbstractMyfoxClient):
        """Initialize the gate object."""
        self._data: SiteData = data
        self._client = client

    @property
    def site_id(self) -> int:
        """Return the site unique identifier of the site."""
        return self._data["siteId"]

    @property
    def label(self) -> str:
        """Return the label of the site."""
        return self._data["label"]

    @property
    def brand(self) -> str:
        """Return the brand of the site."""
        return self._data["brand"]

    @property
    def timezone(self) -> str:
        """Return the timezone of the site."""
        return self._data["timezone"]

    @property
    def axa(self) -> str:
        """Return the AXA Assistance identifier of the site."""
        return self._data["AXA"]

    @property
    def camera_count(self) -> int:
        """Return the number of cameras on the site."""
        return self._data["cameraCount"]

    @property
    def gate_count(self) -> int:
        """Return the number of gates on the site."""
        return self._data["gateCount"]

    @property
    def shutter_count(self) -> int:
        """Return the number of shutters on the site."""
        return self._data["shutterCount"]

    @property
    def socket_count(self) -> int:
        """Return the number of sockets on the site."""
        return self._data["socketCount"]

    @property
    def module_count(self) -> int:
        """Return the number of modules on the site."""
        return self._data["moduleCount"]

    @property
    def heater_count(self) -> int:
        """Return the number of heaters on the site."""
        return self._data["heaterCount"]

    @property
    def scenario_count(self) -> int:
        """Return the number of scenarios on the site."""
        return self._data["scenarioCount"]

    @property
    def device_temperature_count(self) -> int:
        """Return the number of temperature sensors on the site."""
        return self._data["deviceTemperatureCount"]

    @property
    def device_state_count(self) -> int:
        """Return the number of IntelliTag on the site."""
        return self._data["deviceStateCount"]

    @property
    def device_light_count(self) -> int:
        """Return the number of light sensors on the site."""
        return self._data["deviceLightCount"]

    @property
    def device_detector_count(self) -> int:
        """Return the number of generic detectors on the site."""
        return self._data["deviceDetectorCount"]

    async def get_sockets(self) -> list[Socket]:
        """Return the sockets in a site."""
        resp = await self._client._request(
            "get", f"site/{self.site_id}/device/socket/items"
        )
        return [
            Socket(socket_data, self._client, self.site_id)
            for socket_data in (resp.json())["payload"]["items"]
        ]

    async def get_shutters(self) -> list[Shutter]:
        """Return the shutters in a site."""
        resp = await self._client._request(
            "get", f"site/{self.site_id}/device/shutter/items"
        )
        return [
            Shutter(shutter_data, self._client, self.site_id)
            for shutter_data in (resp.json())["payload"]["items"]
        ]

    async def get_electric_groups(self) -> list[ElectricGroup]:
        """Return list group of type electric."""
        resp = await self._client._request(
            "get", f"site/{self.site_id}/group/electric/items"
        )
        return [
            ElectricGroup(group_data, self._client, self.site_id)
            for group_data in (resp.json())["payload"]["items"]
        ]

    async def get_shutter_groups(self) -> list[ShutterGroup]:
        """Return list group of type shutter."""
        resp = await self._client._request(
            "get", f"site/{self.site_id}/group/shutter/items"
        )
        return [
            ShutterGroup(group_data, self._client, self.site_id)
            for group_data in (resp.json())["payload"]["items"]
        ]

    async def get_security(self) -> Security:
        """Return the sockets in a site."""
        resp = await self._client._request("get", f"site/{self.site_id}/security")
        return Security((resp.json())["payload"], self._client, self.site_id)
