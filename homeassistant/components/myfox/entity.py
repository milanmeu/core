"""Base class for Rituals Perfume Genie diffuser entity."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo, Entity

from .aiomyfox import Device, Group, Site
from .const import DOMAIN


class MyfoxEntity(Entity):
    """Representation of a Myfox entity."""

    def __init__(self, myfox_object: Device | Group) -> None:
        """Init hookup site and device."""
        self._myfox_object = myfox_object
        self._attr_name = self._myfox_object.label


class MyfoxDeviceEntity(MyfoxEntity):
    """Representation of a Myfox device entity."""

    _myfox_object: Device

    def __init__(self, device: Device, site: Site) -> None:
        """Init hookup site and device."""
        super().__init__(device)
        device_id = str(self._myfox_object.device_id)
        self._attr_unique_id = device_id
        self._attr_device_info = DeviceInfo(
            name=self._myfox_object.label,
            identifiers={(DOMAIN, device_id)},
            manufacturer=site.brand,
            model=self._myfox_object.model_label,
            via_device=(DOMAIN, str(site.site_id)),
        )


class MyfoxGroupEntity(MyfoxEntity):
    """Representation of a Myfox group entity."""

    _myfox_object: Group

    def __init__(self, group: Group, site: Site) -> None:
        """Init hookup group."""
        super().__init__(group)
        group_id = str(self._myfox_object.group_id)
        self._attr_unique_id = group_id
        self._attr_device_info = DeviceInfo(
            name=self._myfox_object.label,
            identifiers={(DOMAIN, group_id)},
            manufacturer=site.brand,
            model=self._myfox_object.type,
            via_device=(DOMAIN, str(site.site_id)),
        )
