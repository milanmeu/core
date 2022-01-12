"""Support for Nanoleaf binary sensor."""
from __future__ import annotations

import logging

from aionanoleaf import Nanoleaf, Panel

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NanoleafEntryData
from .const import (
    DOMAIN,
    PANEL_SHAPE_ICON,
    SUPPORTED_TOUCH_DEVICE_MODELS,
    UNSUPPORTED_TOUCH_PANEL_MODELS,
)
from .entity import NanoleafTouchEntity

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


class NanoleafPanelBinarySensorEntity(NanoleafTouchEntity, BinarySensorEntity):
    """Representation of a Nanoleaf panel binary sensor entity."""

    _attr_is_on = False
    _should_not_reset_state = "off"

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        icon = PANEL_SHAPE_ICON.get(self._panel.shape, "mdi:shape")
        return icon if self.is_on else f"{icon}-outline"

    def _reset_entity(self) -> None:
        """Reset entity state."""
        self._attr_is_on = False


class NanoleafPanelTouch(NanoleafPanelBinarySensorEntity):
    """Representation of a Nanoleaf panel touch binary sensor entity."""

    def __init__(self, nanoleaf: Nanoleaf, panel: Panel) -> None:
        """Initialize an Nanoleaf panel touch binary sensor."""
        super().__init__(nanoleaf, panel, "Touch")

    def _set_state(self, touch_type: str) -> None:
        """Set the entity state."""
        self._attr_is_on = touch_type == "Hold" or touch_type == "Down"


class NanoleafPanelHover(NanoleafPanelBinarySensorEntity):
    """Representation of a Nanoleaf panel hover binary sensor entity."""

    def __init__(self, nanoleaf: Nanoleaf, panel: Panel) -> None:
        """Initialize an Nanoleaf panel hover binary sensor."""
        super().__init__(nanoleaf, panel, "Hover")

    def _set_state(self, touch_type: str) -> None:
        """Set the entity state."""
        self._attr_is_on = touch_type == "Hover" or touch_type == "Up"
