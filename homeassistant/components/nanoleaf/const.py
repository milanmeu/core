"""Constants for Nanoleaf integration."""

from homeassistant.backports.enum import StrEnum

DOMAIN = "nanoleaf"

NANOLEAF_EVENT = f"{DOMAIN}_event"


class NanoleafTriggers(StrEnum):
    """Triggers for Nanoleaf."""

    LAYOUT_CHANGE = "layout_change"
