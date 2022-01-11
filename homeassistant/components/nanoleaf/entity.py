"""Base class for Nanoleaf entity."""

from aionanoleaf import Nanoleaf, Panel

from homeassistant.const import ATTR_IDENTIFIERS, ATTR_MODEL, ATTR_NAME, ATTR_VIA_DEVICE
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN


class NanoleafEnity(Entity):
    """Representation of a Nanoleaf entity."""

    def __init__(self, nanoleaf: Nanoleaf) -> None:
        """Initialize an Nanoleaf entity."""
        self._nanoleaf = nanoleaf
        self._attr_device_info: DeviceInfo = DeviceInfo(
            manufacturer=nanoleaf.manufacturer,
            sw_version=nanoleaf.firmware_version,
            configuration_url=f"http://{nanoleaf.host}",
        )


class NanoleafDeviceEntity(NanoleafEnity):
    """Representation of a Nanoleaf device entity."""

    def __init__(self, nanoleaf: Nanoleaf) -> None:
        """Initialize an Nanoleaf entity."""
        super().__init__(nanoleaf)
        self._attr_device_info[ATTR_IDENTIFIERS] = {(DOMAIN, nanoleaf.serial_no)}
        self._attr_device_info[ATTR_NAME] = nanoleaf.name
        self._attr_device_info[ATTR_MODEL] = nanoleaf.model


class NanoleafPanelEntity(NanoleafEnity):
    """Representation of a Nanoleaf panel entity."""

    _attr_should_poll = False

    def __init__(self, nanoleaf: Nanoleaf, panel: Panel) -> None:
        """Initialize an Nanoleaf panel entity."""
        super().__init__(nanoleaf)
        self._nanoleaf = nanoleaf
        self._panel = panel
        self._attr_device_info[ATTR_IDENTIFIERS] = {
            (DOMAIN, f"{self._nanoleaf.serial_no}_{self._panel.id}")
        }
        self._attr_device_info[
            ATTR_NAME
        ] = f"{self._nanoleaf.name} {self._panel.shape.name} {self._panel.id}"
        self._attr_device_info[ATTR_MODEL] = self._panel.shape.name
        self._attr_device_info[ATTR_VIA_DEVICE] = (DOMAIN, self._nanoleaf.serial_no)
