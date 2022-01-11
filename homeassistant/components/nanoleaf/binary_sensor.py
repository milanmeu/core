"""Support for Nanoleaf binary sensor."""
from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from asyncio.tasks import Task
import logging

from aionanoleaf import Nanoleaf, Panel

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NanoleafEntryData
from .const import (
    DOMAIN,
    PANEL_SHAPE_ICON,
    SUPPORTED_TOUCH_DEVICE_MODELS,
    UNSUPPORTED_TOUCH_PANEL_MODELS,
)
from .entity import NanoleafPanelEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Nanoleaf binary sensor."""
    entry_data: NanoleafEntryData = hass.data[DOMAIN][entry.entry_id]
    nanoleaf = entry_data.device

    if nanoleaf.model not in SUPPORTED_TOUCH_DEVICE_MODELS:
        _LOGGER.debug(
            "Nanoleaf model '%s' doesn't support touch events", nanoleaf.model
        )
        return

    entities: list[NanoleafPanelBinarySensorEntity] = []
    for panel in nanoleaf.panels:
        if panel.shape not in UNSUPPORTED_TOUCH_PANEL_MODELS:
            entities.append(NanoleafPanelTouch(nanoleaf, panel))
            entities.append(NanoleafPanelHover(nanoleaf, panel))
    async_add_entities(entities)


class NanoleafPanelBinarySensorEntity(NanoleafPanelEntity, BinarySensorEntity, ABC):
    """Representation of a Nanoleaf panel binary sensor entity."""

    _attr_is_on = False
    _reset_task: Task | None = None

    def __init__(self, nanoleaf: Nanoleaf, panel: Panel, sensor_type: str) -> None:
        """Initialize an Nanoleaf binary sensor."""
        super().__init__(nanoleaf, panel)
        self._attr_unique_id = f"{nanoleaf.serial_no}_{panel.id}_{sensor_type}"
        self._attr_name = f"{nanoleaf.name} {panel.shape.name} {panel.id} {sensor_type}"

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        icon = PANEL_SHAPE_ICON.get(self._panel.shape, "mdi:shape")
        return icon if self.is_on else f"{icon}-outline"

    async def _async_set_state(self, value: bool) -> None:
        """Set the entity state."""
        self._attr_is_on = value
        self.async_write_ha_state()
        if self._reset_task is not None and not self._reset_task.done():
            self._reset_task.cancel()
        if self.is_on:
            self._reset_task = asyncio.create_task(self._reset_after_timeout())

    async def _reset_after_timeout(self) -> None:
        """Reset entity state after timeout."""
        # Reset to False if no event is detected for 0.4 seconds
        try:
            await asyncio.sleep(0.4)
        except asyncio.CancelledError:
            return
        self._attr_is_on = False
        self.async_write_ha_state()

    @abstractmethod
    async def _async_handle_touch(self, touch_type: str) -> None:
        """Handle panel touch event."""

    async def async_added_to_hass(self) -> None:
        """Handle entity being added to Home Assistant."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_touch_panel_{self._nanoleaf.serial_no}_{self._panel.id}",
                self._async_handle_touch,
            )
        )


class NanoleafPanelTouch(NanoleafPanelBinarySensorEntity):
    """Representation of a Nanoleaf panel touch binary sensor entity."""

    def __init__(self, nanoleaf: Nanoleaf, panel: Panel) -> None:
        """Initialize an Nanoleaf panel touch binary sensor."""
        super().__init__(nanoleaf, panel, "Touch")

    async def _async_handle_touch(self, touch_type: str) -> None:
        """Handle panel touch event."""
        await self._async_set_state(
            True if touch_type == "Hold" or touch_type == "Down" else False
        )


class NanoleafPanelHover(NanoleafPanelBinarySensorEntity):
    """Representation of a Nanoleaf panel hover binary sensor entity."""

    def __init__(self, nanoleaf: Nanoleaf, panel: Panel) -> None:
        """Initialize an Nanoleaf panel hover binary sensor."""
        super().__init__(nanoleaf, panel, "Hover")

    async def _async_handle_touch(self, touch_type: str) -> None:
        """Handle panel touch event."""
        await self._async_set_state(
            True if touch_type == "Hover" or touch_type == "Up" else False
        )
