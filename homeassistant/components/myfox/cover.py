"""Support for Rituals Perfume Genie switches."""
from __future__ import annotations

from typing import Any

from homeassistant.components.cover import (
    DEVICE_CLASS_SHADE,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    CoverEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .aiomyfox import Shutter, ShutterGroup, Site
from .const import DOMAIN
from .entity import MyfoxDeviceEntity, MyfoxEntity, MyfoxGroupEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the diffuser switch."""
    sites: list[Site] = hass.data[DOMAIN][entry.entry_id]

    entities: list[MyfoxCover] = []
    for site in sites:
        shutters = await site.get_shutters()
        for shutter in shutters:
            entities.append(MyfoxCoverDevice(shutter, site))
        groups = await site.get_shutter_groups()
        for group in groups:
            entities.append(MyfoxCoverGroup(group, site))

    async_add_entities(entities)


class MyfoxCover(MyfoxEntity, RestoreEntity, CoverEntity):
    """Representation of a Myfox cover device."""

    _myfox_object: Shutter | ShutterGroup

    _attr_device_class = DEVICE_CLASS_SHADE
    _attr_assumed_state = True
    _attr_is_closed = False
    _attr_supported_features = SUPPORT_OPEN | SUPPORT_CLOSE

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        self._attr_is_closing = True
        self.async_write_ha_state()
        await self._myfox_object.close()
        self._attr_is_closing = False
        self._attr_is_closed = True
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        self._attr_is_opening = True
        self.async_write_ha_state()
        await self._myfox_object.open()
        self._attr_is_opening = False
        self._attr_is_closed = False
        self.async_write_ha_state()


class MyfoxCoverDevice(MyfoxCover, MyfoxDeviceEntity):
    """Representation of a Myfox cover device."""

    _myfox_object: Shutter

    def __init__(self, device: Shutter, site: Site) -> None:
        """Init the cover device entity."""
        super().__init__(device, site)


class MyfoxCoverGroup(MyfoxCover, MyfoxGroupEntity):
    """Representation of a Myfox cover device."""

    _myfox_object: ShutterGroup

    def __init__(self, group: ShutterGroup, site: Site) -> None:
        """Init the cover group entity."""
        super().__init__(group, site)
