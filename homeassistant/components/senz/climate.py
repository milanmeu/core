"""nVent RAYCHEM SENZ climate platform."""
from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, TEMP_CELSIUS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SENZDataUpdateCoordinator
from .aiosenz import MODE_AUTO, Thermostat
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ATTR_DATETIME = "datetime"
SERVICE_CLIMATE_TIMER = "set_climate_timer"

CLIMATE_TIMER_SCHEMA = {
    vol.Required(ATTR_DATETIME): cv.datetime,
    vol.Optional(ATTR_TEMPERATURE): vol.Coerce(float),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SENZ climate entities from a config entry."""
    coordinator: SENZDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_CLIMATE_TIMER,
        CLIMATE_TIMER_SCHEMA,
        "async_set_timer",
    )

    async_add_entities(
        SENZClimate(thermostat, coordinator) for thermostat in coordinator.data.values()
    )


class SENZClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a SENZ climate entity."""

    _attr_temperature_unit = TEMP_CELSIUS
    _attr_precision = PRECISION_TENTHS
    _attr_hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_AUTO]
    _attr_supported_features = SUPPORT_TARGET_TEMPERATURE
    _attr_max_temp = 35
    _attr_min_temp = 5

    def __init__(
        self,
        thermostat: Thermostat,
        coordinator: SENZDataUpdateCoordinator,
    ) -> None:
        """Init SENZ climate."""
        super().__init__(coordinator)
        self._thermostat = thermostat
        self._attr_name = self._thermostat.name
        self._attr_unique_id = self._thermostat.serial_number
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._thermostat.serial_number)},
            manufacturer="nVent Raychem",
            model="SENZ WIFI",
            name=self._thermostat.name,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._thermostat = self.coordinator.data[self._thermostat.serial_number]
        self.async_write_ha_state()

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self._thermostat.current_temperatue

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self._thermostat.setpoint_temperature

    @property
    def available(self) -> bool:
        """Return True if the thermostat is available."""
        return self._thermostat.online

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. auto, heat mode."""
        if self._thermostat.mode == MODE_AUTO:
            return HVAC_MODE_AUTO
        return HVAC_MODE_HEAT

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_AUTO:
            await self._thermostat.auto()
        else:
            await self._thermostat.manual()
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        _LOGGER.warning(kwargs)
        temp: float = kwargs[ATTR_TEMPERATURE]
        await self._thermostat.manual(temp)
        await self.coordinator.async_request_refresh()

    async def async_set_timer(
        self, datetime: datetime, temperature: float | None = None
    ) -> None:
        """Set thermostat to specified or current temperature for a time period."""
        print(datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        _LOGGER.warning(datetime)
        dt = datetime.replace(tzinfo=timezone.utc)
        print(dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        await self._thermostat.hold(temperature, datetime)
