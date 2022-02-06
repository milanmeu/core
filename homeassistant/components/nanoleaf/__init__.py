"""The Nanoleaf integration."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta

from aionanoleaf import EffectsEvent, InvalidToken, Nanoleaf, StateEvent, Unavailable
from aionanoleaf.events import TouchStreamEvent
from apprise import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_SOCKET_PORT, DOMAIN

PLATFORMS = [Platform.BINARY_SENSOR, Platform.BUTTON, Platform.LIGHT, Platform.SENSOR]


@dataclass
class NanoleafEntryData:
    """Class for sharing data within the Nanoleaf integration."""

    device: Nanoleaf
    coordinator: DataUpdateCoordinator
    event_listener: asyncio.Task


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nanoleaf from a config entry."""
    nanoleaf = Nanoleaf(
        async_get_clientsession(hass), entry.data[CONF_HOST], entry.data[CONF_TOKEN]
    )

    async def async_get_state() -> None:
        """Get the state of the device."""
        try:
            await nanoleaf.get_info()
        except Unavailable as err:
            raise ConfigEntryNotReady from err
        except InvalidToken as err:
            raise ConfigEntryAuthFailed from err

    coordinator = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=nanoleaf.serial_no,
        update_interval=timedelta(minutes=1),
        update_method=async_get_state,
    )

    coordinator.async_config_entry_first_refresh()

    async def update_light_state(event: StateEvent | EffectsEvent) -> None:
        """Receive state and effect event."""
        async_dispatcher_send(hass, f"{DOMAIN}_update_light_{nanoleaf.serial_no}")

    async def touch_stream_callback(event: TouchStreamEvent) -> None:
        """Receive touch stream event."""
        async_dispatcher_send(
            hass,
            f"{DOMAIN}_touch_panel_{nanoleaf.serial_no}_{event.panel_id}",
            event.touch_type,
        )

    event_listener = asyncio.create_task(
        nanoleaf.listen_events(
            state_callback=update_light_state,
            effects_callback=update_light_state,
            touch_stream_callback=touch_stream_callback,
            local_port=entry.options.get(CONF_SOCKET_PORT),
        )
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = NanoleafEntryData(
        nanoleaf, coordinator, event_listener
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    entry_data: NanoleafEntryData = hass.data[DOMAIN].pop(entry.entry_id)
    entry_data.event_listener.cancel()
    return True
