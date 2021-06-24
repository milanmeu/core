"""Config flow for Rituals Perfume Genie integration."""
from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientResponseError
from pyrituals import Account, AuthenticationException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.rituals_perfume_genie.entity import ROOMNAME
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    ACCOUNT_HASH,
    ATTRIBUTES,
    DEVICES,
    DOMAIN,
    HUBLOT,
    CONFIGURED_DEVICES,
    ROOM_ENTITY_DEVICES,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rituals Perfume Genie."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        errors = {}

        session = async_get_clientsession(self.hass)
        account = Account(user_input[CONF_EMAIL], user_input[CONF_PASSWORD], session)

        try:
            await account.authenticate()
        except ClientResponseError:
            errors["base"] = "cannot_connect"
        except AuthenticationException:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(account.data[CONF_EMAIL])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=account.data[CONF_EMAIL],
                data={ACCOUNT_HASH: account.data[ACCOUNT_HASH]},
            )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RitualsOptionsFlowHandler(config_entry)


class RitualsOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Rituals Perfume Genie options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize Rituals Perfume Genie options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage Rituals Perfume Genie options."""
        if user_input is None:
            devices = self.hass.data[DOMAIN][self.config_entry.entry_id][
                DEVICES
            ].values()
            self.configured_devices = self.config_entry.options.get(
                CONFIGURED_DEVICES, []
            )
            room_entity_devices = self.config_entry.options.get(ROOM_ENTITY_DEVICES, [])

            for device in devices:
                if device.hub_data[HUBLOT] not in self.configured_devices:
                    if device.has_battery:
                        # The room size entity is enabled by default for new devices with a battery
                        room_entity_devices.append(device.hub_data[HUBLOT])
                    self.configured_devices.append(device.hub_data[HUBLOT])

            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Optional(
                            ROOM_ENTITY_DEVICES, default=room_entity_devices
                        ): cv.multi_select(
                            {
                                device.hub_data[HUBLOT]: device.hub_data[ATTRIBUTES][
                                    ROOMNAME
                                ]
                                for device in devices
                            }
                        ),
                    }
                ),
            )

        return self.async_create_entry(
            title="", data={CONFIGURED_DEVICES: self.configured_devices, **user_input}
        )
