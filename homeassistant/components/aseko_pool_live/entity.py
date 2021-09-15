"""Aseko entity."""
import logging

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AsekoDataUpdateCoordinator
from .aioaseko import Unit
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AsekoEntity(CoordinatorEntity):
    """Representation of an aseko entity."""

    def __init__(self, unit: Unit, coordinator: AsekoDataUpdateCoordinator) -> None:
        """Initialize the aseko entity."""
        super().__init__(coordinator)
        self._unit = unit

        self._device_model = f"ASIN AQUA {self._unit.type}"
        self._device_name = (
            self._device_model
            if self._unit.name is None or self._unit.name == ""
            else self._unit.name
        )

        self._attr_device_info = DeviceInfo(
            name=self._device_name,
            identifiers={(DOMAIN, str(self._unit.serial_number))},
            manufacturer="Aseko",
            model=self._device_model,
        )

    @property
    def available(self) -> bool:
        """Return if the entity is available."""
        return super().available
