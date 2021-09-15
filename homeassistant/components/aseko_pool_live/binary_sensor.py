"""Support for Aseko Pool Live binary sensors."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_PROBLEM,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AsekoDataUpdateCoordinator
from .aioaseko import Unit
from .const import DOMAIN
from .entity import AsekoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Aseko Pool Live binary sensors."""
    data: list[tuple[Unit, AsekoDataUpdateCoordinator]] = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    entities: list[BinarySensorEntity] = []
    for unit, coordinator in data:
        entities.append(WaterFlowBinarySensorEntity(unit, coordinator))
        entities.append(AlarmBinarySensorEntity(unit, coordinator))
    async_add_entities(entities)


class WaterFlowBinarySensorEntity(AsekoEntity, BinarySensorEntity):
    """Representation of a unit water flow binary sensor entity."""

    def __init__(self, unit: Unit, coordinator: AsekoDataUpdateCoordinator) -> None:
        """Initialize the variable sensor."""
        super().__init__(unit, coordinator)
        self._attr_name = f"{self._device_name} Water Flow"
        self._attr_unique_id = f"{self._unit.serial_number} water flow"
        self._attr_icon = "mdi:waves-arrow-right"

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return self._unit.water_flow


class AlarmBinarySensorEntity(AsekoEntity, BinarySensorEntity):
    """Representation of a unit alarm binary sensor entity."""

    def __init__(self, unit: Unit, coordinator: AsekoDataUpdateCoordinator) -> None:
        """Initialize the variable sensor."""
        super().__init__(unit, coordinator)
        self._attr_name = f"{self._device_name} Alarm"
        self._attr_unique_id = f"{self._unit.serial_number} alarm"
        self._attr_device_class = DEVICE_CLASS_PROBLEM

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return self._unit.has_alarm
