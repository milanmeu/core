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
