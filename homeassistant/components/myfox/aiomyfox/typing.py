"""Myfox types."""
from __future__ import annotations

from typing import Literal, TypedDict

HeaterStateLabel = Literal["on", "off", "eco", "frost", "boost", "away", "auto"]
SecurityLevel = Literal["disarmed", "partial", "armed"]


class SiteData(TypedDict):
    """Site raw data type."""

    siteId: int
    label: str
    brand: str
    timezone: str
    AXA: str
    cameraCount: int
    gateCount: int
    shutterCount: int
    socketCount: int
    moduleCount: int
    heaterCount: int
    scenarioCount: int
    deviceTemperatureCount: int
    deviceStateCount: int
    deviceLightCount: int
    deviceDetectorCount: int


class SecurityData(TypedDict):
    """Security raw data type."""

    status: int
    statusLabel: SecurityLevel


class DeviceData(TypedDict):
    """Device raw data type."""

    deviceId: int
    label: str
    modelId: str
    modelLabel: str


class GateData(DeviceData):
    """Gate raw data type."""


class ShutterData(DeviceData):
    """Shutter raw data type."""


class SocketData(DeviceData):
    """Socket raw data type."""


class ModuleData(DeviceData):
    """Module raw data type."""


class HeaterData(DeviceData):
    """Heater raw data type."""

    lastTemperature: float
    stateLabel: HeaterStateLabel
    modeLabel: str


class GroupData(TypedDict):
    """Group raw data type."""

    groupId: int
    label: str
    type: str


class ShutterGroupData(GroupData):
    """Group raw data type."""

    devices: list[ShutterData]


class ElectricalGroupData(GroupData):
    """Group raw data type."""

    devices: list[SocketData]
