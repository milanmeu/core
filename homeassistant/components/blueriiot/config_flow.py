"""Config flow for Blueriiot integration."""
from homeassistant.helpers import config_entry_flow

from .const import DOMAIN

config_entry_flow.register_webhook_flow(
    DOMAIN,
    "Blueriiot",
    {"docs_url": "https://www.home-assistant.io/integrations/blueriiot/"},
)
