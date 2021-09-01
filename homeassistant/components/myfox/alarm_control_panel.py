"""Support for Myfox Alarm Control Panels."""
from __future__ import annotations

from aiomyfox import (
    SECURITY_LEVEL_ARMED,
    SECURITY_LEVEL_DISARMED,
    SECURITY_LEVEL_PARTIAL,
    Site,
)

from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMED,
    STATE_ALARM_DISARMING,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Myfox Alarm Control Panel."""
    sites: list[Site] = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MyfoxAlarm(site) for site in sites], True)


class MyfoxAlarm(AlarmControlPanelEntity):
    """Representation of a Myfox Alarm Control Panel."""

    _attr_icon = "mdi:security"
    _attr_code_arm_required = False
    _attr_supported_features = SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY

    def __init__(self, site: Site) -> None:
        """Init the Myfox Alarm Control Panel entity."""
        self._site = site
        self._attr_name = site.label
        self._attr_unique_id = str(site.site_id)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self._site.site_id))},
            manufacturer=self._site.brand,
            model="Main unit",
            name=self._site.label,
        )

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        self._attr_state = STATE_ALARM_DISARMING
        self.async_write_ha_state()
        await self._security.set("disarmed")
        self.async_schedule_update_ha_state(True)

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        self._attr_state = STATE_ALARM_ARMING
        self.async_write_ha_state()
        await self._security.set("partial")
        self.async_schedule_update_ha_state(True)

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        self._attr_state = STATE_ALARM_ARMING
        self.async_write_ha_state()
        await self._security.set("armed")
        self.async_schedule_update_ha_state(True)

    async def async_update(self) -> None:
        """Update the state of the alarm."""
        self._security = await self._site.get_security()
        self._attr_state = {
            SECURITY_LEVEL_DISARMED: STATE_ALARM_DISARMED,
            SECURITY_LEVEL_PARTIAL: STATE_ALARM_ARMED_HOME,
            SECURITY_LEVEL_ARMED: STATE_ALARM_ARMED_AWAY,
        }[self._security.status_label]
