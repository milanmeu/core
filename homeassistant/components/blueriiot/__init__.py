"""The Blueriiot integration."""
from __future__ import annotations
from homeassistant.helpers.dispatcher import async_dispatcher_send
import json
import logging
from homeassistant.helpers import config_entry_flow
from homeassistant.const import CONF_WEBHOOK_ID

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DATA_UPDATE

PLATFORMS = ["sensor"]

_LOGGER = logging.getLogger(__name__)


async def handle_webhook(hass: HomeAssistant, webhook_id, request) -> None:
    """Handle webhook callback."""
    body = await request.text()
    try:
        data = json.loads(body) if body else {}
    except ValueError:
        return None
    _LOGGER.warning(data)
    data["webhook_id"] = webhook_id
    hass.bus.async_fire(DATA_UPDATE, data)
    async_dispatcher_send(
        hass,
        "update",
        data,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configure based on config entry."""
    hass.data[DOMAIN] = {
        "devices": set(),
        "unsub_device": {},
    }
    hass.components.webhook.async_register(
        DOMAIN, "Blueriiot", entry.data[CONF_WEBHOOK_ID], handle_webhook
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.components.webhook.async_unregister(entry.data[CONF_WEBHOOK_ID])
    hass.data[DOMAIN]["unsub_device"].pop(entry.entry_id)()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async_remove_entry = config_entry_flow.webhook_async_remove_entry









