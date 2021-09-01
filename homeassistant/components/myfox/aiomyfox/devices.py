"""Socket."""
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AbstractMyfoxClient
    from .typing import (
        DeviceData,
        GateData,
        HeaterData,
        HeaterStateLabel,
        ModuleData,
        ShutterData,
        SocketData,
    )


class Device(ABC):
    """Class that represents an abstract device in the Myfox API."""

    def __init__(
        self, data: DeviceData, client: AbstractMyfoxClient, site_id: int
    ) -> None:
        """Initialize the shutter object."""
        self._data = data
        self._client = client
        self._site_id = site_id

    @property
    def device_id(self) -> int:
        """Return the deviceId of the shutter."""
        return self._data["deviceId"]

    @property
    def label(self) -> str:
        """Return the label of the shutter."""
        return self._data["label"]

    @property
    def model_id(self) -> str:
        """Return the modelId of the shutter."""
        return self._data["modelId"]

    @property
    def model_label(self) -> str:
        """Return the modelLabel of the shutter."""
        return self._data["modelLabel"]


class Gate(Device):
    """Class that represents a gate object in the Myfox API."""

    _data: GateData

    def __init__(
        self, data: GateData, client: AbstractMyfoxClient, site_id: int
    ) -> None:
        """Initialize the gate object."""
        super().__init__(data, client, site_id)

    async def perform_one(self) -> None:
        """Perform action #1."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/gate/perform/one"
        )

    async def perform_two(self) -> None:
        """Perform action #2."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/gate/perform/two"
        )


class Shutter(Device):
    """Class that represents a Shutter in the Myfox API."""

    _data: ShutterData

    def __init__(
        self,
        data: ShutterData,
        client: AbstractMyfoxClient,
        site_id: int,
    ) -> None:
        """Initialize the shutter object."""
        super().__init__(data, client, site_id)

    async def close(self) -> None:
        """Close shutter."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/shutter/close"
        )

    async def open(self) -> None:
        """Open shutter."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/shutter/open"
        )

    async def my(self) -> None:
        """Set shutter to favorite position."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/shutter/my"
        )


class Socket(Device):
    """Class that represents a Socket object in the Myfox API."""

    _data: SocketData

    def __init__(self, data: SocketData, client: AbstractMyfoxClient, site_id: int):
        """Initialize the socket object."""
        super().__init__(data, client, site_id)

    async def off(self) -> None:
        """Turn the socket off."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/socket/off"
        )

    async def on(self) -> None:
        """Turn the socket on."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/socket/on"
        )


class Module(Device):
    """Class that represents a module object in the Myfox API."""

    _data: ModuleData

    def __init__(
        self, data: ModuleData, client: AbstractMyfoxClient, site_id: int
    ) -> None:
        """Initialize the module object."""
        super().__init__(data, client, site_id)

    async def perform_one(self) -> None:
        """Perform action #1."""
        resp = await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/module/perform/one"
        )
        resp.raise_for_status()

    async def perform_two(self) -> None:
        """Perform action #2."""
        resp = await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/module/perform/two"
        )
        resp.raise_for_status()


class Heater(Device):
    """Class that represents a heater object in the Myfox API."""

    _data: HeaterData

    def __init__(self, data: HeaterData, client: AbstractMyfoxClient, site_id: int):
        """Initialize the heater object."""
        super().__init__(data, client, site_id)

    @property
    def last_temperature(self) -> float:
        """Return the lastTemperature of the heater."""
        return self._data["lastTemperature"]

    @property
    def state_label(self) -> HeaterStateLabel:
        """Return the stateLabel of the heater: on, off, eco, frost, boost, away or auto."""
        return self._data["stateLabel"]

    @property
    def mode_label(self) -> str:
        """Return the heater heating mode: boiler or wired."""
        return self._data["modeLabel"]

    async def auto(self) -> None:
        """Set the thermostat to 'auto' mode."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/heater/auto"
        )

    async def away(self) -> None:
        """Set the thermostat to 'away' mode."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/heater/away"
        )

    async def boost(self) -> None:
        """Set the thermostat to 'boost' mode."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/heater/boost"
        )

    async def eco(self) -> None:
        """Set the heater to 'eco' mode."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/heater/eco"
        )

    async def frost(self) -> None:
        """Set the heater to 'frost' mode."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/heater/frost"
        )

    async def off(self) -> None:
        """Set the heater to 'off' mode."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/heater/off"
        )

    async def on(self) -> None:
        """Set the heater to 'on' mode."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/heater/on"
        )

    async def thermostat_off(self) -> None:
        """Set the thermostat to 'off' mode."""
        await self._client._request(
            "post", f"site/{self._site_id}/device/{self.device_id}/heater/off"
        )
