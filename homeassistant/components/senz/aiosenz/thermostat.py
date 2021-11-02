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

"""SENZ theromstat."""
from __future__ import annotations

from datetime import datetime

from .auth import AbstractSENZAuth
from .typing import ThermostatModel

MODE_AUTO = 1
MODE_HOLD = 2
MODE_MANUAL = 3


class Thermostat:
    """Senz Thermostat."""

    def __init__(self, raw_data: ThermostatModel, auth: AbstractSENZAuth) -> None:
        """Initialize the thermostat object."""
        self.raw_data = raw_data
        self.auth = auth

    @property
    def serial_number(self) -> str:
        """Return the thermostats serial number."""
        return self.raw_data["serialNumber"]

    @property
    def name(self) -> str:
        """Return the name of the thermostat."""
        return self.raw_data["name"]

    @property
    def current_temperatue(self) -> float:
        """Return the current registered temperature in celsius."""
        return self.raw_data["currentTemperature"] / 100

    @property
    def online(self) -> bool:
        """Return if the thermostat is online or offline."""
        return self.raw_data["online"]

    @property
    def is_heating(self) -> bool:
        """Return if the thermostat relay is on and set to heat."""
        return self.raw_data["isHeating"]

    @property
    def setpoint_temperature(self) -> float:
        """Return the current setpoint temperature on the thermostat in celsius."""
        return self.raw_data["setPointTemperature"] / 100

    @property
    def hold_until(self) -> str:
        """How long it will hold current mode. If null it will hold indefinetely.

        UTC will always be returned.
        Date format to use: yyyy-MM-ddTHH:mm:ssK.
        """
        return self.raw_data["holdUntil"]

    @property
    def mode(self) -> int:
        """Return the thermostats current mode.

        1 = Auto
        2 = Hold
        3 = Manual
        4+ = Other modes are described in the documentation.
        """
        return self.raw_data["mode"]

    @property
    def error_state(self) -> str | None:
        """Return errors if any are registered."""
        return self.raw_data["errorState"]

    async def auto(self) -> None:
        """Close shutter."""
        await self.auth._request(
            "PUT", "Mode/auto", json={"serialNumber": self.serial_number}
        )

    async def manual(
        self, temperature: float | None = None, absolute: bool = True
    ) -> None:
        """Set thermostat mode to Manual."""
        data: dict[str, str | int] = {"serialNumber": self.serial_number}

        if temperature is not None:
            data["temperature"] = int(temperature * 100)
            data["temperatureType"] = 0 if absolute else 1

        await self.auth._request("put", "Mode/manual", json=data)

    async def hold(
        self,
        temperature: float | None = None,
        hold_until: datetime | None = None,
        absolute: bool = True,
    ) -> None:
        """Set thermostat mode to Hold."""
        data: dict[str, str | int] = {"serialNumber": self.serial_number}

        if hold_until is not None:
            data["holdUntil"] = hold_until.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if temperature is not None:
            data["temperature"] = int(temperature * 100)
            data["temperatureType"] = 0 if absolute else 1

        await self.auth._request("put", "Mode/hold", json=data)
