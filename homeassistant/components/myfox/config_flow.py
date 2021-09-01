"""Config flow for Myfox."""
import logging

from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN


class MyfoxFlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Myfox OAuth2 authentication."""

    DOMAIN = DOMAIN

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)
