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

"""Typing for SENZ."""
from __future__ import annotations

from typing import TypedDict


class AccountModel(TypedDict):
    """Account model."""

    userName: str
    temperatureScale: str
    language: str


class ModeAuto(TypedDict):
    """ModeAuto model."""

    serialNumber: str


class ModeHold(TypedDict):
    """ModeHold model."""

    serialNumber: str
    temperature: int | None
    holdUntil: str | None
    temperatureType: int | None


class ModeManual(TypedDict):
    """ModeManual model."""

    serialNumber: str
    temperature: int | None
    temperatureType: int | None


class ThermostatModel(TypedDict):
    """Thermostat model."""

    serialNumber: str
    name: str
    currentTemperature: int
    online: bool
    isHeating: bool
    setPointTemperature: int
    holdUntil: str
    mode: int
    errorState: str | None
