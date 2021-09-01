"""Support for Myfox switches."""
from __future__ import annotations

from typing import Any

from aiomyfox import ElectricGroup, Site, Socket

from homeassistant.components.switch import DEVICE_CLASS_OUTLET, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MyfoxDeviceEntity, MyfoxEntity, MyfoxGroupEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Myfox switches."""
    sites: list[Site] = hass.data[DOMAIN][entry.entry_id]

    entities: list[MyfoxSwitch] = []
    for site in sites:
        sockets = await site.get_sockets()
        for socket in sockets:
            entities.append(MyfoxSwitchDevice(socket, site))
        groups = await site.get_electric_groups()
        for group in groups:
            entities.append(MyfoxSwitchGroup(group, site))

    async_add_entities(entities)


class MyfoxSwitch(MyfoxEntity, SwitchEntity):
    """Representation of a Myfox switch."""

    _myfox_object: Socket | ElectricGroup

    _attr_device_class = DEVICE_CLASS_OUTLET
    _attr_assumed_state = True
    _attr_is_on = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self._myfox_object.on()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self._myfox_object.off()
        self._attr_is_on = False
        self.async_write_ha_state()


class MyfoxSwitchDevice(MyfoxSwitch, MyfoxDeviceEntity):
    """Representation of a Myfox switch device."""

    _myfox_object: Socket

    def __init__(self, device: Socket, site: Site) -> None:
        """Init the cover entity."""
        super().__init__(device, site)


class MyfoxSwitchGroup(MyfoxSwitch, MyfoxGroupEntity):
    """Representation of a Myfox switch group."""

    _myfox_object: ElectricGroup

    def __init__(self, group: ElectricGroup, site: Site) -> None:
        """Init the cover entity."""
        super().__init__(group, site)
