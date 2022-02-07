"""The Nanoleaf integration."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from aionanoleaf import EffectsEvent, InvalidToken, Nanoleaf, StateEvent, Unavailable
from aionanoleaf.events import LayoutEvent, TouchEvent

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST, CONF_TOKEN, CONF_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, NANOLEAF_EVENT, NanoleafTriggers

PLATFORMS = ["button", "light"]


@dataclass
class NanoleafEntryData:
    """Class for sharing data within the Nanoleaf integration."""

    device: Nanoleaf
    event_listener: asyncio.Task


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nanoleaf from a config entry."""
    nanoleaf = Nanoleaf(
        async_get_clientsession(hass), entry.data[CONF_HOST], entry.data[CONF_TOKEN]
    )
    try:
        await nanoleaf.get_info()
    except Unavailable as err:
        raise ConfigEntryNotReady from err
    except InvalidToken as err:
        raise ConfigEntryAuthFailed from err

    async def _callback_update_light_state(event: StateEvent | EffectsEvent) -> None:
        """Receive state and effect event."""
        async_dispatcher_send(hass, f"{DOMAIN}_update_light_{nanoleaf.serial_no}")

    async def _layout_event_callback(event: LayoutEvent) -> None:
        """Receive layout event."""
        data = {
            CONF_DEVICE_ID: nanoleaf.serial_no,
            CONF_TYPE: NanoleafTriggers.LAYOUT_CHANGE,
        }
        hass.bus.async_fire(NANOLEAF_EVENT, data)

    async def _touch_event_callback(event: TouchEvent) -> None:
        """Receive touch event."""
        data = {
            CONF_DEVICE_ID: nanoleaf.serial_no,
            CONF_TYPE: {
                0: "single_tap",
                1: "double_tap",
                2: "swipe_up",
                3: "swipe_down",
                4: "swipe_left",
                5: "swipe_right",
            }[event.gesture_id],
        }
        hass.bus.async_fire(NANOLEAF_EVENT, data)

    event_listener = asyncio.create_task(
        nanoleaf.listen_events(
            state_callback=_callback_update_light_state,
            effects_callback=_callback_update_light_state,
            layout_callback=_layout_event_callback,
            touch_callback=_touch_event_callback,
        )
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = NanoleafEntryData(
        nanoleaf, event_listener
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    entry_data: NanoleafEntryData = hass.data[DOMAIN].pop(entry.entry_id)
    entry_data.event_listener.cancel()
    return True
