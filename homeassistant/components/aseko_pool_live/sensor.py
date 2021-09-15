"""Support for Aseko Pool Live sensors."""
from __future__ import annotations

from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEVICE_CLASS_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AsekoDataUpdateCoordinator
from .aioaseko import Unit, Variable
from .const import DOMAIN
from .entity import AsekoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Aseko Pool Live sensors."""
    data: list[tuple[Unit, AsekoDataUpdateCoordinator]] = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    entities = []
    for unit, coordinator in data:
        for variable in unit.variables:
            entities.append(VariableSensorEntity(unit, variable, coordinator))
    async_add_entities(entities)


class VariableSensorEntity(AsekoEntity, SensorEntity):
    """Representation of a unit variable sensor entity."""

    attr_state_class = STATE_CLASS_MEASUREMENT

    def __init__(
        self, unit: Unit, variable: Variable, coordinator: AsekoDataUpdateCoordinator
    ) -> None:
        """Initialize the variable sensor."""
        super().__init__(unit, coordinator)
        self._variable = variable

        variable_name = {
            "Water temp.": "Water Temperature",
            "Air temp.": "Air Temperature",
            "Cl free": "Free Chlorine",
        }.get(self._variable.name, self._variable.name)

        self._attr_name = f"{self._device_name} {variable_name}"
        self._attr_unique_id = f"{self._unit.serial_number}{self._variable.type}"
        self._attr_native_unit_of_measurement = self._variable.unit

        self._attr_icon = {
            "ph": "mdi:ph",
            "rx": "mdi:flask",
            "waterLevel": "mdi:waves",
            "clf": "mdi:test-tube",
        }.get(self._variable.type)

        self._attr_device_class = {
            "waterTemp": DEVICE_CLASS_TEMPERATURE,
            "airTemp": DEVICE_CLASS_TEMPERATURE,
        }.get(self._variable.type)

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        variable: Variable = self.coordinator.data[self._variable.type]
        return variable.current_value
